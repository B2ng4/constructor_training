import os
from typing import Optional
from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configs(BaseSettings):
    """Главный конфиг проекта"""

    # ------------ Настройки проекта ------------
    PROJECT_NAME: str = "Конструктор Тренингов"
    PROJECT_DESCRIPTION: str = (
        "веб-сервис Конструктор тренингов. \nТестовый пользователь: test@example.com string"
    )

    # ------------ Веб-сервер ------------
    HOST: str = Field(default="localhost", env="HOST")
    SERVER_HOST: str = Field(default="", env="SERVER_HOST")
    PORT: int = 8003

    # ------------ Логирование ------------
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # ------------ Аутентификация ------------
    SECRET_KEY: str = Field(
        default="your-secret-key", env="SECRET_KEY"
    )  # Секретный ключ для JWT и шифрования
    ALGORITHM: str = Field(
        default="HS256", env="ALGORITHM"
    )  # Алгоритм шифрования для JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=720, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )  # Время жизни токена

    # ------------ Окружение ------------
    # Создавать ли тестового пользователя test@example.com при пустой БД.
    SEED_TEST_USER: bool = Field(default=False, env="SEED_TEST_USER")
    # CORS: список origin через запятую, либо "*" (без credentials).
    CORS_ORIGINS: str = Field(default="*", env="CORS_ORIGINS")

    # ------------ БД ------------
    DB_HOST: Optional[str] = Field(default="localhost", env="DB_HOST")
    DB_PORT: Optional[int] = Field(default=5432, env="DB_PORT")
    DB_USER: Optional[str] = Field(default="postgres", env="DB_USER")
    DB_NAME: Optional[str] = Field(default="postgres", env="DB_NAME")
    DB_PASS: Optional[str] = Field(default="admin", env="DB_PASS")

    # ------------ MinIO хранилище ----------------------------------------
    MINIO_ROOT_USER: Optional[str] = Field(
        default="minioadmin", env="MINIO_ROOT_USER"
    )
    MINIO_ROOT_PASSWORD: Optional[str] = Field(
        default="minioadmin", env="MINIO_ROOT_PASSWORD"
    )
    MINIO_BUCKET: Optional[str] = Field(default="trainings", env="MINIO_BUCKET")
    MINIO_ENDPOINT_URL: Optional[str] = Field(
        default="http://localhost:9000", env="MINIO_ENDPOINT_URL"
    )

    # ------------------- AI Video Analysis ---------------------------------
    AI_API_KEY: Optional[str] = Field(default="AI_API_KEY", env="AI_API_KEY")
    AI_BASE_URL: Optional[str] = Field(
        default="https://routerai.ru/api/v1", env="AI_BASE_URL"
    )
    # https://api.vsellm.ru/v1
    # https://routerai.ru/api/v1"
    # default="qwen/qwen3-vl-30b-a3b-instruct"
    # Instruct без «thinking»: быстрее и предсказуемее JSON для шагов (см. каталог VseLLM).
    AI_MODEL: Optional[str] = Field(
        default="qwen/qwen3-vl-30b-a3b-instruct", env="AI_MODEL"
    )
    # Сколько кадров в секунду «видит» VL-модель при разборе (больше — точнее быстрые клики, тяжелее запрос).
    AI_VIDEO_FPS: int = Field(default=4, env="AI_VIDEO_FPS")

    AI_VIDEO_FPS_MAX: int = Field(default=12, env="AI_VIDEO_FPS_MAX")

    # Перед отправкой в AI всегда собирать облегчённое видео (разрешение + разрежение кадров).
    # Иначе в модель уходит полный исходник (десятки MB base64) — долго и хуже стабильность разбора UI.
    AI_VIDEO_ALWAYS_ANALYSIS_PROXY: bool = Field(
        default=True, env="AI_VIDEO_ALWAYS_ANALYSIS_PROXY"
    )
    AI_VIDEO_ANALYSIS_MAX_SIDE: int = Field(
        default=960, env="AI_VIDEO_ANALYSIS_MAX_SIDE"
    )
    AI_VIDEO_ANALYSIS_ENCODE_FPS: int = Field(
        default=6, env="AI_VIDEO_ANALYSIS_ENCODE_FPS"
    )
    AI_VIDEO_ANALYSIS_JPEG_QUALITY: int = Field(
        default=54, env="AI_VIDEO_ANALYSIS_JPEG_QUALITY"
    )

    # Потолок размера base64 при отправке видео в AI (байты строки base64).
    # Большие исходные файлы сжимаются в VideoCompressor; лимит нужен как страховка для API.
    AI_VIDEO_MAX_BASE64_BYTES: int = Field(
        default=250_000_000, env="AI_VIDEO_MAX_BASE64_BYTES"
    )
    # Целевой потолок до отправки в VL (меньше — быстрее и меньше 5xx у провайдера).
    # Сжатие дожимает прокси, пока оценка base64 не станет не выше этого значения (и не выше MAX).
    AI_VIDEO_SOFT_BASE64_BYTES: int = Field(
        default=22_000_000, env="AI_VIDEO_SOFT_BASE64_BYTES"
    )

    AI_VIDEO_FRAME_OFFSET_SEC: float = Field(
        default=0.10, env="AI_VIDEO_FRAME_OFFSET_SEC"
    )
    # Сдвиг вперёд при извлечении кадра «после» (анимации/переходы UI успели завершиться).
    AI_VIDEO_AFTER_FRAME_LAG_SEC: float = Field(
        default=0.12, env="AI_VIDEO_AFTER_FRAME_LAG_SEC"
    )

    # ------------------- AI Voice (SaluteSpeech) ---------------------------
    CLIENT_ID_SALUTESPEECH: str = Field(default="", env="CLIENT_ID_SALUTESPEECH")
    SALUT_SPEECH_AUTORIZATION: str = Field(default="", env="SALUT_SPEECH_AUTORIZATION")

    # ------------------- YOLO UI-детекция -----------------------------------
    # Авторазметка кликабельных элементов на загружаемых скриншотах.
    YOLO_UI_DETECTION_ENABLED: bool = Field(
        default=True, env="YOLO_UI_DETECTION_ENABLED"
    )
    YOLO_UI_CONF: float = Field(default=0.25, env="YOLO_UI_CONF")
    YOLO_MODEL_REPO: str = Field(
        default="macpaw-research/yolov11l-ui-elements-detection",
        env="YOLO_MODEL_REPO",
    )
    YOLO_MODEL_FILE: str = Field(
        default="ui-elements-detection.pt", env="YOLO_MODEL_FILE"
    )

    # ------------------- Фоновые задачи (Celery + Redis) -------------------
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0", env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND"
    )

    # ------------------- OAuth Yandex ID -----------------------------------
    YANDEX_CLIENT_ID: str = Field(default="", env="YANDEX_CLIENT_ID")
    YANDEX_CLIENT_SECRET: str = Field(
        default="",
        validation_alias=AliasChoices("YANDEX_CLIENT_SECRET", "CLIENT_SECRET"),
    )
    YANDEX_REDIRECT_URI: str = Field(
        default="http://localhost:8002/auth/yandex/callback",
        env="YANDEX_REDIRECT_URI",
    )
    FRONTEND_PUBLIC_URL: str = Field(
        default="http://localhost:5173",
        env="FRONTEND_PUBLIC_URL",
    )

    @model_validator(mode="after")
    def _yandex_redirect_non_empty(self) -> "Configs":
        if not (self.YANDEX_REDIRECT_URI or "").strip():
            self.YANDEX_REDIRECT_URI = "http://localhost:8002/auth/yandex/callback"
        return self

    @model_validator(mode="after")
    def _secret_key_not_default(self) -> "Configs":
        """Слабый/дефолтный SECRET_KEY заменяется случайным — иначе JWT подделываются."""
        weak = {"", "your-secret-key", "your-secret-key-change-in-production", "secret"}
        if (self.SECRET_KEY or "").strip().lower() in weak:
            import secrets
            import logging

            logging.getLogger("configs").warning(
                "SECRET_KEY не задан или дефолтный — сгенерирован случайный. "
                "Все JWT инвалидируются при каждом рестарте. "
                "Задайте SECRET_KEY в backend/.env"
            )
            self.SECRET_KEY = secrets.token_urlsafe(48)
        return self

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        extra="ignore",
    )


configs = Configs()


def get_db_url():
    user = quote_plus(str(configs.DB_USER or "postgres"))
    password = quote_plus(str(configs.DB_PASS or ""))
    host = configs.DB_HOST or "localhost"
    port = configs.DB_PORT or 5432
    name = configs.DB_NAME or "postgres"
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


def get_auth_data():
    return {"secret_key": configs.SECRET_KEY, "algorithm": configs.ALGORITHM}


def get_frontend_base_url() -> str:
    """Базовый URL фронтенда для внешних ссылок; фолбэк — SERVER_HOST."""
    return (configs.FRONTEND_PUBLIC_URL or configs.SERVER_HOST or "").rstrip("/")


def public_passage_link(access_token: str) -> str:
    """Полная публичная ссылка прохождения тренинга."""
    return f"{get_frontend_base_url()}/training/passage/{access_token}"
