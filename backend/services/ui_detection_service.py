"""
Детекция кликабельных UI-элементов на скриншотах (YOLOv11 UI-elements).

Модель: macpaw-research/yolov11l-ui-elements-detection (Hugging Face).
Модель и тяжёлые зависимости (torch/ultralytics) загружаются лениво при первом
вызове, чтобы не замедлять старт приложения и не ломать окружения без torch.
"""

import io
import threading
from typing import Dict, List

from core.config import configs
from core.logging_config import logger

# Перевод классов модели на русский (для подписей в редакторе)
CLASS_TRANSLATION = {
    "AXButton": "Кнопка",
    "AXButtons": "Кнопка",
    "AXImage": "Изображение",
    "AXImages": "Изображение",
}


def _translate_class(class_name: str) -> str:
    return CLASS_TRANSLATION.get(class_name, class_name)


class UIDetectionService:
    """Ленивый синглтон-обёртка над YOLO-моделью детекции UI-элементов."""

    def __init__(self) -> None:
        self._model = None
        self._model_path = None
        self._lock = threading.Lock()
        self._load_failed = False

    @property
    def enabled(self) -> bool:
        return bool(getattr(configs, "YOLO_UI_DETECTION_ENABLED", False))

    def _ensure_model(self):
        if self._model is not None:
            return self._model
        if self._load_failed:
            return None
        with self._lock:
            if self._model is not None:
                return self._model
            if self._load_failed:
                return None
            try:
                from huggingface_hub import hf_hub_download
                from ultralytics import YOLO

                self._model_path = hf_hub_download(
                    repo_id=configs.YOLO_MODEL_REPO,
                    filename=configs.YOLO_MODEL_FILE,
                )
                self._model = YOLO(self._model_path)
                logger.info(
                    "YOLO UI-детектор загружен: {} ({})",
                    configs.YOLO_MODEL_REPO,
                    self._model_path,
                )
            except Exception as e:
                self._load_failed = True
                logger.error("Не удалось загрузить YOLO UI-детектор: {}", e)
                return None
        return self._model

    def detect_elements(self, image_bytes: bytes) -> List[Dict]:
        """
        Возвращает список детекций в пикселях исходного изображения:
        [{x, y, width, height, class_name, class_ru, conf}, ...]
        """
        if not self.enabled:
            return []

        model = self._ensure_model()
        if model is None:
            return []

        try:
            from PIL import Image

            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            with self._lock:
                results = model.predict(
                    img, conf=configs.YOLO_UI_CONF, verbose=False
                )

            detections: List[Dict] = []
            for result in results:
                names = result.names
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().tolist())
                    cls_id = int(box.cls[0].cpu().item())
                    conf = float(box.conf[0].cpu().item())
                    class_name = names[cls_id]
                    w = x2 - x1
                    h = y2 - y1
                    if w <= 0 or h <= 0:
                        continue
                    detections.append(
                        {
                            "x": x1,
                            "y": y1,
                            "width": w,
                            "height": h,
                            "class_name": class_name,
                            "class_ru": _translate_class(class_name),
                            "conf": round(conf, 4),
                        }
                    )

            # Сортировка сверху вниз, слева направо — стабильный порядок в UI
            detections.sort(key=lambda d: (d["y"], d["x"]))
            logger.info("YOLO UI-детекция: найдено {} элементов", len(detections))
            return detections
        except Exception as e:
            logger.error("Ошибка YOLO UI-детекции: {}", e)
            return []


ui_detection_service = UIDetectionService()
