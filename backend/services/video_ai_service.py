import base64
import json
import re
import tempfile
import os
import cv2
import numpy as np
import httpx
from typing import List, Dict, Optional
from dataclasses import dataclass
from fastapi import UploadFile, HTTPException, status
from openai import OpenAI

from core.config import configs
from core.logging_config import logger


ANALYSIS_PROMPT = """
Ты - эксперт по анализу видео интерфейсов программ. Твоя задача - найти все действия пользователя и ТОЧНО определить области элементов интерфейса.

Проанализируй видео и найди все значимые действия (клики по кнопкам, выбор меню, ввод текста, переключение опций).

ВАЖНО ПРО ОБЛАСТИ (bbox):
1. Область должна ТОЧНО обводить элемент интерфейса (кнопку, поле, пункт меню)
2. НЕ делай область слишком большой - она должна быть минимальной вокруг элемента
3. Смотри на момент ПЕРЕД действием - когда курсор подходит к элементу, но еще не кликнул
4. Если видишь курсор около элемента - область должна быть вокруг ЭЛЕМЕНТА, а не вокруг курсора
5. Для кнопок - обведи только саму кнопку с небольшим отступом
6. Для полей ввода - обведи всё поле полностью
7. Для пунктов меню - обведи текст пункта меню
8. Координаты в формате normalized bbox [x_min, y_min, x_max, y_max], где:
   - x_min, x_max: от 0 (левый край) до 1 (правый край экрана)
   - y_min, y_max: от 0 (верхний край) до 1 (нижний край экрана)
   - Пример: кнопка в центре экрана размером ~10% ширины и ~5% высоты будет [0.45, 0.475, 0.55, 0.525]

Для каждого действия укажи:
- Таймкод в формате ММ:СС (момент, когда действие НАЧИНАЕТСЯ)
- Вопрос в формате "Как ...?" (например: "Как нажать кнопку Сохранить?", "Как открыть меню Файл?")
- Точную область элемента интерфейса в виде bbox [x_min, y_min, x_max, y_max]

Верни ТОЛЬКО JSON без дополнительного текста:
{"00:00": {"question": "Как открыть меню?", "bbox": [0.02, 0.05, 0.12, 0.08]}, "00:05": {"question": "Как нажать кнопку?", "bbox": [0.45, 0.48, 0.55, 0.52]}}
"""


@dataclass
class VideoStepData:
    """Результат AI-анализа одного шага из видео."""
    timecode: str
    question: str
    bbox: List[float]
    frame_bytes: bytes
    frame_width: int
    frame_height: int


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

    async def analyze_video(self, video_file: UploadFile) -> List[VideoStepData]:
        """
        Полный пайплайн:
        1. Сохраняет видео во временный файл
        2. Отправляет видео в AI-модель для анализа
        3. Парсит ответ (таймкоды, описания, bbox)
        4. Извлекает кадры по таймкодам
        5. Возвращает список VideoStepData
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await video_file.read())
            video_path = tmp.name

        try:
            ai_response = self._call_ai_model(video_path)
            steps_json = self._parse_ai_response(ai_response)

            if not steps_json:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="AI-модель не смогла распознать действия в видео",
                )

            results = self._extract_frames_at_timecodes(video_path, steps_json)
            return results

        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)

    def _call_ai_model(self, video_path: str) -> str:
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
                            "video_url": {"url": f"data:video/mp4;base64,{base64_video}"},
                            "fps": self.fps,
                        },
                        {"type": "text", "text": ANALYSIS_PROMPT},
                    ],
                }
            ],
            max_tokens=4000,
            temperature=0.1,
        )

        return completion.choices[0].message.content

    def _parse_ai_response(self, raw_response: str) -> Dict:
        """
        Парсит JSON из ответа AI-модели.
        Модель может обернуть JSON в markdown-блок — обрабатываем это.
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
                    return {}
            else:
                return {}

        if not isinstance(data, dict):
            return {}

        validated = {}
        for timecode, value in data.items():
            if not isinstance(value, dict):
                continue
            question = value.get("question", "")
            bbox = value.get("bbox", [])
            if not question or not isinstance(bbox, list) or len(bbox) != 4:
                logger.warning(f"Пропущен шаг {timecode}: некорректные данные")
                continue
            try:
                bbox = [float(b) for b in bbox]
            except (ValueError, TypeError):
                logger.warning(f"Пропущен шаг {timecode}: некорректный формат bbox")
                continue
            
            # Валидация bbox
            bbox = [max(0.0, min(1.0, b)) for b in bbox]
            
            # Проверка что bbox имеет корректные размеры (не перевернут, не слишком маленький/большой)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            
            if width <= 0 or height <= 0:
                logger.warning(f"Пропущен шаг {timecode}: некорректные размеры bbox (width={width}, height={height})")
                continue
            
            if width < 0.01 or height < 0.01:
                logger.warning(f"Пропущен шаг {timecode}: bbox слишком маленький (width={width}, height={height})")
                continue
                
            if width > 0.9 or height > 0.9:
                logger.warning(f"Пропущен шаг {timecode}: bbox слишком большой (width={width}, height={height})")
                continue
            
            logger.info(f"Шаг {timecode}: question='{question}', bbox={bbox}, size=({width:.3f}x{height:.3f})")
            validated[timecode] = {"question": question, "bbox": bbox}

        return validated

    def _timecode_to_seconds(self, timecode: str) -> float:
        """Конвертирует ММ:СС в секунды."""
        parts = timecode.strip().split(":")
        try:
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            else:
                return 0
        except ValueError:
            return 0

    def _extract_frames_at_timecodes(
        self, video_path: str, steps_json: Dict
    ) -> List[VideoStepData]:
        """
        Извлекает кадры из видео по таймкодам из AI-ответа.
        Кадр берётся за FRAME_OFFSET_SEC секунд ДО указанного таймкода,
        чтобы показать состояние экрана перед действием.
        """
        FRAME_OFFSET_SEC = 2.5

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Не удалось открыть видеофайл",
            )

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        results: List[VideoStepData] = []

        sorted_timecodes = sorted(steps_json.keys(), key=self._timecode_to_seconds)

        for timecode in sorted_timecodes:
            step_info = steps_json[timecode]
            action_seconds = self._timecode_to_seconds(timecode)

            target_seconds = max(0, action_seconds - FRAME_OFFSET_SEC)

            if target_seconds > duration:
                target_seconds = max(0, duration - 0.5)

            target_ms = target_seconds * 1000.0
            cap.set(cv2.CAP_PROP_POS_MSEC, target_ms)
            ret, frame = cap.read()

            if not ret or frame is None:
                frame_number = int(target_seconds * fps)
                frame_number = max(0, min(frame_number, total_frames - 1))
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ret, frame = cap.read()
                if not ret or frame is None:
                    logger.warning(f"Не удалось извлечь кадр для таймкода {timecode}")
                    continue

            height, width = frame.shape[:2]
            ok, buf = cv2.imencode(".png", frame)
            if not ok:
                continue

            results.append(
                VideoStepData(
                    timecode=timecode,
                    question=step_info["question"],
                    bbox=step_info["bbox"],
                    frame_bytes=buf.tobytes(),
                    frame_width=width,
                    frame_height=height,
                )
            )

        cap.release()
        return results
