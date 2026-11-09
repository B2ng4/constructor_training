import base64
import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import cv2
import httpx
import numpy as np
from fastapi import HTTPException, UploadFile, status
from openai import OpenAI

from core.config import configs
from core.logging_config import logger

ANALYSIS_PROMPT = """
Ты анализируешь СКРИНКАСТ (запись экрана) обучающего видео по работе с программным обеспечением.
Твоя задача: составить точный пошаговый JSON для интерактивного тренинга-симулятора.

Для каждого видимого действия пользователя (клик, двойной клик, правый клик, ввод текста, горячие клавиши) создай отдельный шаг.

Анализируемый период: {start_time:.1f} - {end_time:.1f} секунд.

Верни ТОЛЬКО JSON:
{{
  "steps": [
    {{
      "timecode": "MM:SS",
      "seconds": 12.5,
      "title": "Краткий заголовок (максимум 5 слов) НА РУССКОМ ЯЗЫКЕ",
      "instruction": "Чёткая инструкция для пользователя НА РУССКОМ ЯЗЫКЕ (начинается с глагола)",
      "action_type": "left_click|right_click|double_click|text_input|key_chord",
      "bbox": [x1, y1, x2, y2],
      "expected_text": "текст для ввода (только для text_input)",
      "key_chord": ["ctrl", "s"]
    }}
  ]
}}

Размер кадра видео: {frame_w}x{frame_h} пикселей.

ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:
1. title начинается с глагола действия на русском.
2. timecode_before в формате "MM:SS.mmm" — кадр непосредственно перед действием.
3. timecode_after в формате "MM:SS.mmm" — стабильный кадр после действия.
4. bbox — АБСОЛЮТНЫЕ ПИКСЕЛИ кадра {frame_w}x{frame_h}, целые числа [x1, y1, x2, y2], минимальный прямоугольник вокруг целевого элемента. НЕ нормализуй координаты.
5. action_type строго по фактическому действию.
6. text_input -> expected_text обязателен.
7. key_chord -> key_chord обязателен.
8. Не создавай шаг при неизвестном bbox или неразличимом действии.
9. Всегда добавляй финальный шаг: title="Тренинг завершен", bbox=[0,0,0,0]
"""

FALLBACK_ANALYSIS_PROMPT = """
Проанализируй видео-скринкаст и создай JSON шагов интерактивного тренинга.
Верни ТОЛЬКО JSON без markdown и комментариев:
{
  "steps": [
    {
      "timecode_before": "MM:SS.mmm",
      "timecode_after": "MM:SS.mmm",
      "title": "[Глагол] [объект] НА РУССКОМ ЯЗЫКЕ",
      "instruction_md": "Краткая инструкция НА РУССКОМ ЯЗЫКЕ.",
      "interaction": {
        "type": "left_click|right_click|double_click|hover|text_input|key_chord",
        "bbox": [x1, y1, x2, y2]  // АБСОЛЮТНЫЕ ПИКСЕЛИ кадра, целые числа, НЕ 0..1
        "expected_text": null,
        "key_chord": null
      }
    }
  ]
}
"""

REPAIR_JSON_PROMPT = """
Предыдущий ответ не удалось разобрать как JSON. Проанализируй то же видео ещё раз.
Верни ТОЛЬКО один JSON-объект:
{"steps":[{"timecode_before":"M:SS.mmm","timecode_after":"M:SS.mmm","title":"Название шага НА РУССКОМ","instruction_md":"Инструкция НА РУССКОМ","interaction":{"type":"left_click","bbox":[120,240,200,320]}}]}
bbox — АБСОЛЮТНЫЕ ПИКСЕЛИ кадра видео [x1,y1,x2,y2], целые числа, НЕ 0..1.
"""

MAX_FRAME_SIDE = 1280
COMPRESSED_FPS = 4
JPEG_QUALITY = 60


@dataclass
class VideoStepData:
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
        out: List[str] = []
        for x in raw:
            if x is None:
                continue
            s = str(x).strip().lower()
            if s:
                out.append(s)
        return out or None
    return None


class VideoCompressor:
    def __init__(self, max_base64_bytes: int) -> None:
        self.MAX_BASE64_BYTES = max(1, int(max_base64_bytes))

    @staticmethod
    def _estimate_b64_size(file_path: str) -> int:
        return (os.path.getsize(file_path) * 4) // 3

    def _encode_video(
        self, video_path: str, target_fps: int, max_side: int, jpeg_quality: int
    ) -> str:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Не удалось открыть видеофайл для перекодирования",
            )
        src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        scale = min(max_side / max(orig_width, orig_height, 1), 1.0)
        new_width = max((int(orig_width * scale) // 2) * 2, 2)
        new_height = max((int(orig_height * scale) // 2) * 2, 2)
        frame_step = max(1, int(round(src_fps / target_fps)))
        tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".avi")
        tmp_out.close()
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        writer = cv2.VideoWriter(
            tmp_out.name, fourcc, float(target_fps), (new_width, new_height)
        )
        if not writer.isOpened():
            cap.release()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать VideoWriter для сжатия",
            )
        frame_idx = 0
        written = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_step == 0:
                if scale < 1.0:
                    frame = cv2.resize(
                        frame, (new_width, new_height), interpolation=cv2.INTER_AREA
                    )
                ok, buf = cv2.imencode(
                    ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
                )
                if ok:
                    frame = cv2.imdecode(buf, cv2.IMREAD_COLOR)
                    writer.write(frame)
                    written += 1
            frame_idx += 1
        cap.release()
        writer.release()
        logger.info(
            f"Перекодировано: {written} кадров @ {target_fps}fps, {new_width}x{new_height}, качество={jpeg_quality}"
        )
        return tmp_out.name

    def compress_video(self, video_path: str) -> Tuple[str, float, float]:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Не удалось открыть видеофайл для сжатия",
            )
        original_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / original_fps if original_fps > 0 else 0
        cap.release()
        target_fps = COMPRESSED_FPS
        max_side = MAX_FRAME_SIDE
        crf = 23
        out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            str(crf),
            "-r",
            str(target_fps),
            "-vf",
            f"scale={max_side}:-2",
            "-an",
            out_path,
        ]
        try:
            logger.info(
                f"Compressing video: {duration:.1f}s @ {target_fps}fps, max side {max_side}px"
            )
            subprocess.run(cmd, capture_output=True, timeout=120, check=True)
            out_size = os.path.getsize(out_path)
            out_b64_size = (out_size * 4) // 3
            logger.info(
                f"Compressed: {out_size / 1024 / 1024:.2f} MB -> ~{out_b64_size / 1024 / 1024:.2f} MB base64"
            )
            return out_path, original_fps, float(target_fps)
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Video compression failed: {e}",
            ) from e

    def read_as_base64(self, video_path: str) -> Tuple[str, str]:
        ext = os.path.splitext(video_path)[1].lower()
        mime_map = {
            ".mp4": "video/mp4",
            ".avi": "video/avi",
            ".mov": "video/quicktime",
            ".webm": "video/webm",
        }
        mime = mime_map.get(ext, "video/mp4")
        with open(video_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("utf-8")
        logger.info(
            f"Base64 size for API: {len(b64) // 1024}KB (limit {self.MAX_BASE64_BYTES // 1024}KB)"
        )
        return mime, b64


class VideoAIService:
    def __init__(self):
        self._check_ffmpeg()
        self.client = OpenAI(
            api_key=configs.AI_API_KEY,
            base_url=configs.AI_BASE_URL,
            timeout=httpx.Timeout(300.0, connect=30.0),
            max_retries=2,
        )
        self.model = configs.AI_MODEL
        self.compressor = VideoCompressor(configs.AI_VIDEO_MAX_BASE64_BYTES)

    def _check_ffmpeg(self) -> None:
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            logger.info("FFmpeg found")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error("FFmpeg not found!")
            raise RuntimeError("FFmpeg is required but not installed") from e

    async def analyze_video(self, video_file: UploadFile) -> List[VideoStepData]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await video_file.read())
            original_path = tmp.name
        return await self._analyze_video_path(original_path, cleanup_original=True)

    async def analyze_video_path(self, original_path: str) -> List[VideoStepData]:
        # Совместимость с воркером: путь уже лежит в S3 temp.
        return await self._analyze_video_path(original_path, cleanup_original=False)

    async def _analyze_video_path(
        self, original_path: str, cleanup_original: bool
    ) -> List[VideoStepData]:
        start_timestamp = time.time()
        compressed_path: Optional[str] = None
        try:
            cap = cv2.VideoCapture(original_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            logger.info(
                f"Analyzing video: 0.0s - {duration:.1f}s (duration {duration:.1f}s)"
            )
            compressed_path, source_file_fps, compressed_fps = (
                self.compressor.compress_video(original_path)
            )
            analysis_frame_size: Optional[Tuple[int, int]] = None
            cap_compressed = cv2.VideoCapture(compressed_path)
            if cap_compressed.isOpened():
                aw = int(cap_compressed.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
                ah = int(cap_compressed.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
                if aw > 0 and ah > 0:
                    analysis_frame_size = (aw, ah)
            cap_compressed.release()
            fw_prompt, fh_prompt = (analysis_frame_size or (0, 0))
            prompt_with_time = ANALYSIS_PROMPT.format(
                start_time=0,
                end_time=duration,
                frame_w=fw_prompt or "ширина",
                frame_h=fh_prompt or "высота",
            )
            logger.info(
                f"Sending to AI: fps {source_file_fps:.1f}→{compressed_fps:.1f}"
            )
            ai_response = self._call_ai_model(compressed_path, prompt=prompt_with_time)
            steps_payload = self._parse_ai_response(ai_response)
            if not steps_payload:
                logger.warning(
                    "Primary AI response has no valid steps, trying fallback"
                )
                ai_response = self._call_ai_model(
                    compressed_path, prompt=FALLBACK_ANALYSIS_PROMPT
                )
                steps_payload = self._parse_ai_response(ai_response)
                if not steps_payload:
                    logger.warning("Fallback failed, trying repair prompt")
                    ai_response = self._call_ai_model(
                        compressed_path, prompt=REPAIR_JSON_PROMPT
                    )
                    steps_payload = self._parse_ai_response(ai_response)
                    if not steps_payload:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="AI did not return valid steps. Check logs.",
                        )
            # Критично для точности: извлекаем кадры из того же (сжатого) файла,
            # который анализировала модель. Тогда bbox и скрин в одной системе координат.
            frame_source_path = (
                compressed_path
                if compressed_path and os.path.exists(compressed_path)
                else original_path
            )
            use_remap = frame_source_path == original_path
            logger.info(
                f"Frame source for step screenshots: {'compressed' if frame_source_path == compressed_path else 'original'}"
            )
            results = self._extract_frames_at_timecodes(
                frame_source_path,
                steps_payload,
                analysis_frame_size=analysis_frame_size if use_remap else None,
            )
            processing_time = time.time() - start_timestamp
            logger.info(
                f"Analysis completed: {len(results)} steps in {processing_time:.1f}s"
            )
            return results
        finally:
            if compressed_path and os.path.exists(compressed_path):
                try:
                    os.unlink(compressed_path)
                except OSError:
                    pass
            if cleanup_original and os.path.exists(original_path):
                try:
                    os.unlink(original_path)
                except OSError:
                    pass

    def _call_ai_model(
        self, video_path: str, prompt: str, max_tokens: int = 8000
    ) -> str:
        mime, base64_video = self.compressor.read_as_base64(video_path)
        limit = self.compressor.MAX_BASE64_BYTES
        if len(base64_video) > limit:
            logger.warning(
                f"Base64 ({len(base64_video) // 1024}KB) выше потолка ({limit // 1024}KB)"
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Video too large after compression. Please use shorter video.",
            )
        logger.info(f"Sending to AI: {len(base64_video) // 1024}KB, model={self.model}")
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "video_url",
                                "video_url": {
                                    "url": f"data:{mime};base64,{base64_video}"
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.0,
            )
            if hasattr(completion, "usage") and completion.usage:
                logger.info(
                    f"Token usage: prompt={completion.usage.prompt_tokens}, "
                    f"completion={completion.usage.completion_tokens}, "
                    f"total={completion.usage.total_tokens}"
                )
            content = completion.choices[0].message.content
            if content is None:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI returned empty response",
                )
            return content
        except Exception as e:
            logger.exception(f"AI call failed (model={self.model})")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI service error: {str(e)}",
            ) from e

    @staticmethod
    def _strip_model_noise(text: str) -> str:
        if not text:
            return ""
        t = text.strip()
        t = re.sub(
            r"<(?:redacted_)?thinking>[\s\S]*?</(?:redacted_)?thinking>",
            "",
            t,
            flags=re.IGNORECASE,
        )
        return t.strip()

    def _parse_ai_response(self, raw_response: str) -> List[Dict[str, Any]]:
        text = self._strip_model_noise(raw_response)
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

    def _normalize_instruction_md(self, raw: str) -> str:
        s = str(raw or "").strip()
        if not s:
            return ""
        s = s.replace("\\r\\n", "\n").replace("\\n", "\n")
        s = re.sub(r"\s*(##\s+)", r"\n\n\1", s)
        s = re.sub(r"(##\s*(?:Цель|Действие|Контекст|Результат|Шаг))\s+", r"\1\n\n", s)
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
            seconds_raw = item.get("seconds")
            seconds_value: Optional[float] = None
            try:
                if seconds_raw is not None:
                    seconds_value = float(seconds_raw)
            except (TypeError, ValueError):
                seconds_value = None
            timecode_before = tb or legacy_tc
            timecode_after = ta
            timecode = timecode_before
            title = str(item.get("title", "")).strip()
            instruction_md = self._normalize_instruction_md(
                item.get("instruction_md", item.get("instruction", ""))
            )

            action_type = item.get("action_type")
            bbox = item.get("bbox")
            expected_text = item.get("expected_text")
            key_chord = _normalize_key_chord(item.get("key_chord"))

            if action_type:
                itype = _normalize_interaction_type(str(action_type))
            else:
                inter = item.get("interaction")
                if isinstance(inter, dict):
                    itype = _normalize_interaction_type(
                        str(inter.get("type", "left_click"))
                    )
                    bbox = self._coerce_bbox(inter.get("bbox")) or bbox
                    expected_text = inter.get("expected_text") or expected_text
                    key_chord = (
                        _normalize_key_chord(inter.get("key_chord")) or key_chord
                    )
                else:
                    itype = "left_click"

            if bbox is not None and isinstance(bbox, list) and len(bbox) == 4:
                try:
                    bbox = [float(v) for v in bbox]
                except (ValueError, TypeError):
                    bbox = None
            else:
                bbox = None

            if bbox and len(bbox) == 4 and all(v == 0 for v in bbox):
                validated.append(
                    {
                        "timecode": timecode,
                        "timecode_before": timecode_before,
                        "timecode_after": timecode_after or None,
                        "seconds": seconds_value,
                        "title": title or "Тренинг завершен",
                        "instruction_md": instruction_md
                        or "Все действия выполнены. Тренинг завершен",
                        "interaction_type": "left_click",
                        "bbox": [0, 0, 0, 0],
                        "expected_text": None,
                        "key_chord": None,
                    }
                )
                continue

            if not timecode_before or not isinstance(bbox, list) or len(bbox) != 4:
                logger.warning(
                    f"Пропущен шаг: некорректный timecode_before/timecode или bbox: {timecode_before}, {bbox}"
                )
                continue
            if not instruction_md and not title:
                logger.warning(f"Пропущен шаг {timecode_before}: нет текста задания")
                continue

            x1, y1, x2, y2 = bbox
            bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
            is_norm = all(0.0 <= b <= 1.0 for b in bbox)
            if is_norm:
                bbox = [max(0.0, min(1.0, b)) for b in bbox]
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                if width <= 0 or height <= 0:
                    continue
                if width < 0.005 or height < 0.005:
                    logger.warning(
                        f"Шаг {timecode_before}: bbox очень маленький ({width:.3f}x{height:.3f}), пропуск"
                    )
                    continue
                if width > 0.95 or height > 0.95:
                    logger.warning(
                        f"Шаг {timecode_before}: bbox слишком большой ({width:.3f}x{height:.3f}), пропуск"
                    )
                    continue
            else:
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                if width < 2.0 or height < 2.0:
                    logger.warning(
                        f"Шаг {timecode_before}: bbox в пикселях слишком мал ({width:.0f}x{height:.0f}), пропуск"
                    )
                    continue
                if width > 8192 or height > 8192:
                    logger.warning(
                        f"Шаг {timecode_before}: bbox в пикселях нереалистичен ({width:.0f}x{height:.0f}), пропуск"
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
                    "seconds": seconds_value,
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

    def _legacy_dict_to_steps(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            if width > 0.95 or height > 0.95:
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

    def _frame_to_png_bytes(self, frame: Any) -> Optional[bytes]:
        ok, buf = cv2.imencode(".png", frame)
        return buf.tobytes() if ok else None

    def _timecode_to_seconds_precise(self, timecode: str) -> float:
        if not timecode:
            return 0.0
        timecode = timecode.strip().replace(",", ".")
        timecode = re.sub(r"\s+", "", timecode)
        try:
            if ":" in timecode:
                parts = timecode.split(":")
                if len(parts) == 2:
                    minutes = int(parts[0])
                    seconds = float(parts[1])
                    return minutes * 60 + seconds
                if len(parts) == 3:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = float(parts[2])
                    return hours * 3600 + minutes * 60 + seconds
            return float(timecode)
        except (ValueError, TypeError):
            return 0.0

    def _extract_frame_at_time_precise(
        self, video_path: str, seconds: float
    ) -> Optional[bytes]:
        """Извлекает кадр максимально точно: сначала по индексу кадра, затем fallback по msec."""
        if seconds < 0:
            return None
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        # Основной путь: точный seek по номеру кадра.
        frame_idx = int(round(max(0.0, seconds) * fps))
        if total > 0:
            frame_idx = max(0, min(frame_idx, total - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        # Fallback: seek по времени.
        if not ret or frame is None:
            cap.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000.0)
            ret, frame = cap.read()
        cap.release()
        if ret and frame is not None:
            ok, buf = cv2.imencode(".png", frame)
            return buf.tobytes() if ok else None
        return None

    def _remap_bbox_pixels_to_original(
        self,
        bbox: List[float],
        analysis_frame_size: Optional[Tuple[int, int]],
        target_w: int,
        target_h: int,
    ) -> List[float]:
        """Если bbox в пикселях анализа (сжатое видео), масштабируем в размеры оригинального кадра."""
        if not bbox or len(bbox) != 4:
            return bbox
        if max(bbox) <= 1.0:
            # Нормализованные 0..1 не требуют ремапа.
            return bbox
        if not analysis_frame_size:
            return bbox
        src_w, src_h = analysis_frame_size
        if src_w <= 0 or src_h <= 0 or target_w <= 0 or target_h <= 0:
            return bbox
        if src_w == target_w and src_h == target_h:
            return bbox
        sx = target_w / float(src_w)
        sy = target_h / float(src_h)
        x1, y1, x2, y2 = bbox
        mapped = [x1 * sx, y1 * sy, x2 * sx, y2 * sy]
        logger.info(
            f"Remap bbox pixels {bbox} ({src_w}x{src_h} -> {target_w}x{target_h}) => "
            f"{[round(v, 2) for v in mapped]}"
        )
        return mapped

    def _extract_frames_at_timecodes(
        self,
        video_path: str,
        steps_payload: List[Dict[str, Any]],
        analysis_frame_size: Optional[Tuple[int, int]] = None,
    ) -> List[VideoStepData]:
        after_lag_sec = max(0.0, float(configs.AI_VIDEO_AFTER_FRAME_LAG_SEC))
        before_offset = float(getattr(configs, "AI_VIDEO_FRAME_OFFSET_SEC", 0.0) or 0.0)
        logger.info(f"Frame before offset is {before_offset:.3f}s")
        results: List[VideoStepData] = []
        for step in steps_payload:
            tc_before = step.get("timecode_before") or step.get("timecode", "")
            tc_after = step.get("timecode_after")
            bbox = step["bbox"]
            # Если AI дал точные секунды (float), используем их как приоритет,
            # иначе fallback на timecode_before/timecode.
            seconds_from_ai = step.get("seconds")
            if isinstance(seconds_from_ai, (int, float)):
                before_seconds = max(0.0, float(seconds_from_ai))
            else:
                before_seconds = self._timecode_to_seconds_precise(tc_before)
            target_before = max(0.0, before_seconds + before_offset)
            logger.info(
                f"Step frame select: tc={tc_before}, seconds={before_seconds:.3f}, "
                f"target_before={target_before:.3f}"
            )
            png_before = self._extract_frame_at_time_precise(video_path, target_before)
            if png_before is None:
                logger.warning(f"Не удалось извлечь кадр для таймкода {tc_before}")
                continue
            img = cv2.imdecode(np.frombuffer(png_before, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                continue
            height, width = img.shape[:2]
            bbox = self._remap_bbox_pixels_to_original(
                bbox=bbox,
                analysis_frame_size=analysis_frame_size,
                target_w=width,
                target_h=height,
            )
            after_bytes: Optional[bytes] = None
            if tc_after:
                after_seconds = (
                    self._timecode_to_seconds_precise(tc_after) + after_lag_sec
                )
                if after_seconds <= before_seconds:
                    after_seconds = before_seconds + 0.15
                after_bytes = self._extract_frame_at_time_precise(
                    video_path, after_seconds
                )
            results.append(
                VideoStepData(
                    timecode=tc_before,
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
        return results

    async def rewrite_task_text(self, text: str) -> str:
        prompt = (
            "Улучши следующий текст описания/инструкции шага для интерактивного тренинга. "
            "Сделай его понятным и кратким, исправь опечатки и используй уместную Markdown-разметку. "
            "Можешь добавить немного эмодзи для живости. "
            "Верни ТОЛЬКО улучшенный текст на РУССКОМ ЯЗЫКЕ без вступительных фраз.\n\n"
            f"Исходный текст:\n{text}"
        )
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7,
        )
        result = (completion.choices[0].message.content or "").strip()
        for prefix in ("```markdown", "```md", "```"):
            if result.startswith(prefix):
                result = result[len(prefix) :]
                break
        if result.endswith("```"):
            result = result[:-3]
        return result.strip()

    def stream_rewrite_task_text(self, text: str):
        prompt = (
            "Улучши следующий текст описания/инструкции шага для интерактивного тренинга. "
            "Сделай его понятным и кратким, исправь опечатки и используй уместную Markdown-разметку. "
            "Можешь добавить немного эмодзи для живости. "
            "Верни ТОЛЬКО улучшенный текст на РУССКОМ ЯЗЫКЕ.\n\n"
            f"Исходный текст:\n{text}"
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7,
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
