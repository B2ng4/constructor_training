import base64
import json
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import cv2
import httpx
from fastapi import HTTPException, UploadFile, status
from openai import OpenAI

from core.config import configs
from core.logging_config import logger

ANALYSIS_PROMPT = """
Сделай JSON шагов из видео для интерактивного тренинга (скринкаст ПО).

Верни только JSON:
{
  "steps": [
    {
      "timecode_before": "MM:SS",
      "timecode_after": "MM:SS",
      "title": "Короткое название шага",
      "instruction_md": "Короткая инструкция (1-3 предложения) без заголовков.",
      "interaction": {
        "type": "left_click|right_click|double_click|hover|text_input|key_chord",
        "bbox": [x1, y1, x2, y2],
        "expected_text": null,
        "key_chord": null
      }
    }
  ]
}

Жесткие правила:
- timecode_before: момент на шкале видео, где интерфейс ещё НЕ изменён — стабильный кадр ПЕРЕД действием пользователя.
- timecode_after: первый момент ПОСЛЕ действия, когда новый интерфейс уже виден (после анимаций/загрузки), стабильный кадр.
- timecode_after > timecode_before; между ними — само действие (клик, ввод, хоткей).
- bbox только для кадра timecode_before: нормализован 0..1, x1<x2, y1<y2. Обведи МИНИМАЛЬНУЮ зону: кнопку, иконку, поле ввода, чекбокс — не весь экран и не целое окно, если достаточно элемента.
- тип interaction строго по фактическому действию в видео (не угадывай left_click если был двойной клик).
- для text_input обязательно expected_text (точная строка с экрана, пробелы/переносы как в поле).
- для key_chord обязательно key_chord как массив латиницей, например ["ctrl","s"].
- для остальных expected_text=null и key_chord=null.
- таймкоды с долями секунды при необходимости (например 1:05.3).
- если границы шага или bbox неочевидны — шаг не добавляй.
"""

FALLBACK_ANALYSIS_PROMPT = """
Проанализируй видео и верни только JSON со списком шагов.

Формат:
{
  "steps": [
    {
      "timecode_before": "ММ:СС",
      "timecode_after": "ММ:СС",
      "title": "Короткое название",
      "instruction_md": "Короткая инструкция на русском",
      "interaction": {
        "type": "left_click|right_click|double_click|hover|text_input|key_chord",
        "bbox": [x1, y1, x2, y2],
        "expected_text": null,
        "key_chord": null
      }
    }
  ]
}

Правила:
- steps непустой; у каждого шага bbox 0..1 на кадре ДО действия (timecode_before).
- timecode_before — стабильный кадр до действия; timecode_after — стабильный кадр после изменения UI.
- Для text_input expected_text обязателен и не пустой.
- Без markdown-блоков и комментариев, только JSON.
"""


@dataclass
class VideoStepData:
    """Результат AI-анализа одного шага из видео (симулятор)."""

    timecode: str
    instruction_md: str
    step_title: str
    bbox: List[float]
    frame_bytes: bytes
    frame_width: int
    frame_height: int
    action_type_key: str
    expected_text: Optional[str] = None
    key_chord: Optional[List[str]] = None
    timecode_before: Optional[str] = None
    timecode_after: Optional[str] = None
    after_frame_bytes: Optional[bytes] = None


def _normalize_interaction_type(raw: str) -> str:
    r = (raw or "left_click").strip().lower()
    aliases = {
        "leftclick": "left_click",
        "left_click": "left_click",
        "rightclick": "right_click",
        "right_click": "right_click",
        "doubleclick": "double_click",
        "double_click": "double_click",
        "input_text": "text_input",
        "text_input": "text_input",
        "key_press": "key_chord",
        "keychord": "key_chord",
        "key_chord": "key_chord",
        "hover": "hover",
        "click": "left_click",
        "left": "left_click",
        "right": "right_click",
        "double": "double_click",
        "type_text": "text_input",
        "typing": "text_input",
        "input": "text_input",
        "keyboard": "key_chord",
        "hotkey": "key_chord",
    }
    if r in aliases:
        return aliases[r]
    allowed = {
        "left_click",
        "right_click",
        "double_click",
        "hover",
        "text_input",
        "key_chord",
    }
    return r if r in allowed else "left_click"


def _normalize_key_chord(raw: Any) -> Optional[List[str]]:
    if raw is None:
        return None
    if isinstance(raw, str):
        parts = re.split(r"[\s+,]+", raw.strip().lower())
        return [p for p in parts if p]
    if isinstance(raw, list):
        out = []
        for x in raw:
            if x is None:
                continue
            s = str(x).strip().lower()
            if s:
                out.append(s)
        return out or None
    return None


class VideoAIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=configs.AI_API_KEY,
            base_url=configs.AI_BASE_URL,
            timeout=httpx.Timeout(300.0, connect=30.0),
            max_retries=2,
        )
        self.model = configs.AI_MODEL
        self.fps = configs.AI_VIDEO_FPS
        self.fps_max = max(1, int(configs.AI_VIDEO_FPS_MAX or 12))

    def _effective_api_fps(self) -> int:
        return max(1, min(int(round(float(self.fps or 1))), self.fps_max))

    async def analyze_video(self, video_file: UploadFile) -> List[VideoStepData]:
        """
        Полный пайплайн:
        1. Сохраняет видео во временный файл
        2. Отправляет видео в AI-модель для анализа
        3. Парсит ответ (шаги, bbox, типы действий)
        4. Извлекает кадры по таймкодам
        5. Возвращает список VideoStepData
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await video_file.read())
            video_path = tmp.name

        try:
            api_fps = self._effective_api_fps()
            ai_response = self._call_ai_model(video_path, fps=api_fps, max_tokens=4800)
            steps_payload = self._parse_ai_response(ai_response)

            if not steps_payload:
                logger.warning(
                    "Первичный ответ AI не дал валидных шагов, запускаем fallback"
                )
                ai_response = self._call_ai_model(
                    video_path,
                    prompt=FALLBACK_ANALYSIS_PROMPT,
                    fps=api_fps,
                    max_tokens=6400,
                )
                steps_payload = self._parse_ai_response(ai_response)
                if not steps_payload:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="AI-модель не смогла распознать действия в видео",
                    )

            results = self._extract_frames_at_timecodes(video_path, steps_payload)
            return results

        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)

    def _call_ai_model(
        self,
        video_path: str,
        prompt: Optional[str] = None,
        fps: Optional[int] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Кодирует видео в base64 и отправляет в AI-модель."""
        with open(video_path, "rb") as f:
            base64_video = base64.b64encode(f.read()).decode("utf-8")

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "video_url",
                            "video_url": {
                                "url": f"data:video/mp4;base64,{base64_video}"
                            },
                            "fps": fps if fps is not None else self.fps,
                        },
                        {"type": "text", "text": prompt or ANALYSIS_PROMPT},
                    ],
                }
            ],
            max_tokens=max_tokens if max_tokens is not None else 8000,
            temperature=0.0,
        )

        return completion.choices[0].message.content

    def _parse_ai_response(self, raw_response: str) -> List[Dict[str, Any]]:
        """
        Парсит JSON из ответа AI. Поддерживает:
        - новый формат: {"steps": [...]}
        - устаревший: {"00:00": {"question", "bbox"}}
        """
        text = raw_response.strip()

        code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if code_block:
            text = code_block.group(1).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    return []
            else:
                return []

        if isinstance(data, list):
            return self._validate_steps_list(data)

        if not isinstance(data, dict):
            return []

        if isinstance(data.get("steps"), list):
            return self._validate_steps_list(data["steps"])
        if isinstance(data.get("data"), dict) and isinstance(
            data["data"].get("steps"), list
        ):
            return self._validate_steps_list(data["data"]["steps"])
        if isinstance(data.get("result"), dict) and isinstance(
            data["result"].get("steps"), list
        ):
            return self._validate_steps_list(data["result"]["steps"])
        if isinstance(data.get("actions"), list):
            return self._validate_steps_list(data["actions"])

        return self._legacy_dict_to_steps(data)

    def _coerce_bbox(self, raw: Any) -> Optional[List[float]]:
        """
        Поддержка bbox как:
        - [x1, y1, x2, y2]
        - {"x1","y1","x2","y2"}
        - {"left","top","right","bottom"}
        - {"x","y","width","height"}  -> x2=x+width, y2=y+height
        """
        if isinstance(raw, list) and len(raw) == 4:
            try:
                return [float(v) for v in raw]
            except (TypeError, ValueError):
                return None

        if not isinstance(raw, dict):
            return None

        def _get(*keys):
            for k in keys:
                if k in raw and raw[k] is not None:
                    return raw[k]
            return None

        x1 = _get("x1", "xmin", "left")
        y1 = _get("y1", "ymin", "top")
        x2 = _get("x2", "xmax", "right")
        y2 = _get("y2", "ymax", "bottom")
        if None not in (x1, y1, x2, y2):
            try:
                return [float(x1), float(y1), float(x2), float(y2)]
            except (TypeError, ValueError):
                return None

        x = _get("x")
        y = _get("y")
        w = _get("w", "width")
        h = _get("h", "height")
        if None not in (x, y, w, h):
            try:
                xf, yf, wf, hf = float(x), float(y), float(w), float(h)
                return [xf, yf, xf + wf, yf + hf]
            except (TypeError, ValueError):
                return None
        return None

    def _normalize_bbox_scale(self, bbox: List[float]) -> List[float]:
        """
        Приводит bbox к нормализованному виду 0..1.
        Модель может вернуть:
        - 0..1 (нормализованный)
        - 0..100 (проценты)
        """
        if not bbox or len(bbox) != 4:
            return bbox
        if all(0.0 <= b <= 100.0 for b in bbox) and any(b > 1.0 for b in bbox):
            return [b / 100.0 for b in bbox]
        return bbox

    def _normalize_instruction_md(self, raw: str) -> str:
        s = str(raw or "").strip()
        if not s:
            return ""
        # Модель иногда отдаёт \n как текст, а не реальный перенос.
        s = s.replace("\\r\\n", "\n").replace("\\n", "\n")
        # Нормализуем заголовки, если пришли «в одну строку».
        s = re.sub(r"\s*(##\s+)", r"\n\n\1", s)
        s = re.sub(r"(##\s*(?:Цель|Действие|Контекст|Результат|Шаг))\s+", r"\1\n\n", s)
        # Часто модель пишет " - " в одной строке; переводим в markdown-список.
        s = re.sub(r"\s-\s", "\n- ", s)
        s = re.sub(r"\n{3,}", "\n\n", s).strip()
        return s

    def _validate_steps_list(self, steps: Any) -> List[Dict[str, Any]]:
        if not isinstance(steps, list):
            return []

        validated: List[Dict[str, Any]] = []
        for item in steps:
            if not isinstance(item, dict):
                continue
            tb = str(item.get("timecode_before", "")).strip()
            ta = str(item.get("timecode_after", "")).strip()
            legacy_tc = str(item.get("timecode", "")).strip()
            timecode_before = tb or legacy_tc
            timecode_after = ta
            timecode = timecode_before
            instruction_md = self._normalize_instruction_md(
                item.get("instruction_md", "")
            )
            inter = item.get("interaction")
            # Поддержка «плоского» ответа модели:
            # {type, bbox, expected_text, key_chord} без вложенного interaction.
            if not isinstance(inter, dict):
                inter = item

            itype = _normalize_interaction_type(
                str(inter.get("type") or inter.get("interaction_type") or "left_click")
            )
            bbox = self._coerce_bbox(inter.get("bbox"))
            expected_text = inter.get("expected_text")
            key_chord = _normalize_key_chord(inter.get("key_chord"))

            if not timecode_before or not isinstance(bbox, list) or len(bbox) != 4:
                logger.warning("Пропущен шаг: некорректный timecode_before/timecode или bbox")
                continue

            if not instruction_md and not title:
                logger.warning(
                    f"Пропущен шаг {timecode_before}: нет текста задания"
                )
                continue

            try:
                bbox = [float(b) for b in bbox]
            except (ValueError, TypeError):
                continue

            bbox = self._normalize_bbox_scale(bbox)
            # На случай перепутанного порядка координат.
            x1, y1, x2, y2 = bbox
            bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
            bbox = [max(0.0, min(1.0, b)) for b in bbox]
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            if width <= 0 or height <= 0:
                continue
            if width < 0.005 or height < 0.005:
                logger.warning(
                    f"Шаг {timecode_before}: bbox очень маленький, пропуск"
                )
                continue
            if width > 0.95 or height > 0.95:
                logger.warning(
                    f"Шаг {timecode_before}: bbox слишком большой, пропуск"
                )
                continue

            if itype == "text_input":
                if expected_text is not None:
                    expected_text = (
                        str(expected_text)
                        .replace("\r\n", "\n")
                        .replace("\r", "\n")
                        .replace("\\n", "\n")
                        .strip()
                        or None
                    )
                if not expected_text:
                    logger.warning(
                        f"Пропущен шаг {timecode_before}: text_input без expected_text"
                    )
                    continue
            else:
                expected_text = None

            if itype != "key_chord":
                key_chord = None

            if not title and instruction_md:
                title = instruction_md.split("\n", 1)[0].strip("# ")[:120]

            validated.append(
                {
                    "timecode": timecode,
                    "timecode_before": timecode_before,
                    "timecode_after": timecode_after or None,
                    "title": title or f"Шаг {len(validated) + 1}",
                    "instruction_md": instruction_md
                    or title
                    or "Выполните действие на экране.",
                    "interaction_type": itype,
                    "bbox": bbox,
                    "expected_text": expected_text,
                    "key_chord": key_chord,
                }
            )

        return validated

    def _legacy_dict_to_steps(self, data: Dict) -> List[Dict[str, Any]]:
        """Старый формат: таймкод -> {question, bbox}."""
        validated: List[Dict[str, Any]] = []
        for timecode, value in data.items():
            if not isinstance(value, dict):
                continue
            question = value.get("question", "")
            bbox = value.get("bbox", [])
            if not question or not isinstance(bbox, list) or len(bbox) != 4:
                continue
            try:
                bbox = [float(b) for b in bbox]
            except (ValueError, TypeError):
                continue
            bbox = [max(0.0, min(1.0, b)) for b in bbox]
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            if width <= 0 or height <= 0:
                continue
            if width < 0.01 or height < 0.01:
                continue
            if width > 0.9 or height > 0.9:
                continue
            q = str(question).strip()
            tc = str(timecode).strip()
            validated.append(
                {
                    "timecode": tc,
                    "timecode_before": tc,
                    "timecode_after": None,
                    "title": q[:120] if q else "Шаг",
                    "instruction_md": q,
                    "interaction_type": "left_click",
                    "bbox": bbox,
                    "expected_text": None,
                    "key_chord": None,
                }
            )
        return validated

    def _timecode_to_seconds(self, timecode: str) -> float:
        """Конвертирует ММ:СС(.ms) или ЧЧ:ММ:СС(.ms) в секунды."""
        parts = timecode.strip().split(":")
        try:
            if len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            return 0
        except ValueError:
            return 0

    def _frame_to_png_bytes(self, frame: Any) -> Optional[bytes]:
        ok, buf = cv2.imencode(".png", frame)
        return buf.tobytes() if ok else None

    def _read_frame_at_seconds(
        self,
        cap: cv2.VideoCapture,
        target_seconds: float,
        fps: float,
        total_frames: int,
        duration: float,
    ) -> Any:
        """Возвращает BGR-кадр или None."""
        ts = max(0.0, float(target_seconds))
        if duration and ts > duration:
            ts = max(0.0, duration - 0.05)

        frame_number = int(round(ts * fps))
        if total_frames > 0:
            frame_number = max(0, min(frame_number, total_frames - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if not ret or frame is None:
            cap.set(cv2.CAP_PROP_POS_MSEC, ts * 1000.0)
            ret, frame = cap.read()
        return frame if ret and frame is not None else None

    def _extract_frames_at_timecodes(
        self, video_path: str, steps_payload: List[Dict[str, Any]]
    ) -> List[VideoStepData]:
        """Извлекает кадры «до» и опционально «после» по шагам."""
        frame_lead_sec = max(0.0, float(configs.AI_VIDEO_FRAME_OFFSET_SEC))
        after_lag_sec = max(0.0, float(configs.AI_VIDEO_AFTER_FRAME_LAG_SEC))

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Не удалось открыть видеофайл",
            )

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps else 0

        results: List[VideoStepData] = []

        sorted_steps = sorted(
            steps_payload,
            key=lambda s: self._timecode_to_seconds(s["timecode"]),
        )

        for step in sorted_steps:
            timecode = step["timecode"]
            tc_before = step.get("timecode_before") or timecode
            tc_after = step.get("timecode_after")
            bbox = step["bbox"]

            before_seconds = self._timecode_to_seconds(tc_before)
            target_before = max(0.0, before_seconds - frame_lead_sec)

            frame = self._read_frame_at_seconds(
                cap, target_before, fps, total_frames, duration
            )
            if frame is None:
                logger.warning(
                    f"Не удалось извлечь кадр «до» для таймкода {tc_before}"
                )
                continue

            height, width = frame.shape[:2]
            png_before = self._frame_to_png_bytes(frame)
            if not png_before:
                continue

            after_bytes: Optional[bytes] = None
            if tc_after:
                after_seconds = self._timecode_to_seconds(tc_after) + after_lag_sec
                if after_seconds <= before_seconds:
                    after_seconds = before_seconds + 0.15
                if duration and after_seconds > duration - 0.04:
                    after_seconds = max(target_before, duration - 0.04)
                frame_after = self._read_frame_at_seconds(
                    cap, after_seconds, fps, total_frames, duration
                )
                if frame_after is not None:
                    after_png = self._frame_to_png_bytes(frame_after)
                    if after_png and after_png != png_before:
                        after_bytes = after_png
                    elif after_png == png_before:
                        logger.warning(
                            f"Кадры до/после совпали для шага {tc_before}, "
                            "timecode_after уточните в видео"
                        )

            results.append(
                VideoStepData(
                    timecode=timecode,
                    instruction_md=step["instruction_md"],
                    step_title=step["title"],
                    bbox=bbox,
                    frame_bytes=png_before,
                    frame_width=width,
                    frame_height=height,
                    action_type_key=step["interaction_type"],
                    expected_text=step.get("expected_text"),
                    key_chord=step.get("key_chord"),
                    timecode_before=tc_before,
                    timecode_after=tc_after,
                    after_frame_bytes=after_bytes,
                )
            )

        cap.release()
        return results
