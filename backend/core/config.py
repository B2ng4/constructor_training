from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os


class Configs(BaseSettings):


    # ------------ Настройки проекта ------------
    PROJECT_NAME: str = "TrainingKnastu"
    PROJECT_DESCRIPTION: str = "веб-сервис Конструктор тренингов"


    # ------------ Веб-сервер ------------
    HOST:str = "localhost"
    PORT:int = 8002

    # ------------ Аутентификация ------------
    SECRET_KEY: str = Field(
        default="your-secret-key", env="SECRET_KEY"
    )  # Секретный ключ для JWT и шифрования
    ALGORITHM: str = Field(
        default="HS256", env="ALGORITHM"
    )  # Алгоритм шифрования для JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )  # Время жизни токена

    # ------------ БД ------------
    DB_HOST: Optional[str] = Field(default="localhost", env="DB_HOST")
    DB_PORT: Optional[int] = Field(default=5432, env="DB_PORT")
    DB_USER: Optional[str] = Field(default="postgres", env="DB_USER")
    DB_NAME: Optional[str] = Field(default="postgres", env="DB_NAME")
    DB_PASS: Optional[str] = Field(default="admin", env="DB_PASS")

    # ------------ Почта (оповещение) ------------
    MAIL_USERNAME: Optional[str] = Field(
        default="timsidorin@gmail.com", env="MAIL_USERNAME"
    )
    MAIL_PASSWORD: Optional[str] = Field(
        default="xdfj qlia vmpy gskl", env="MAIL_PASSWORD"
    )
    MAIL_FROM: Optional[str] = Field(default="timsidorin@gmail.com", env="MAIL_FROM")
    MAIL_PORT: Optional[int] = Field(default=587, env="MAIL_PORT")
    MAIL_SERVER: Optional[str] = Field(default="smtp.gmail.com", env="MAIL_SERVER")
    MAIL_STARTTLS: bool = Field(default=True, env="MAIL_STARTTLS")
    MAIL_SSL_TLS: bool = Field(default=False, env="MAIL_SSL_TLS")

    # Настройки OAUTH2


    # ------------ S3 хранилище ------------
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default="ASBZAQIUA7VOLQU0DDTD", env="AWS_ACCESS_KEY_ID"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default="GFsM7bTRHbQ4CoZVDCmKsP19Lt8FN0ipQpl5OnTM", env="AWS_SECRET_ACCESS_KEY"
    )
    S3_BUCKET_NAME: Optional[str] = Field(
        default="d08d3831-edc9b373-5fab-42f0-9e2f-441c90348394", env="S3_BUCKET_NAME"
    )
    S3_ENDPOINT_URL: Optional[str] = Field(
        default="https://s3.twcstorage.ru/", env="S3_ENDPOINT_URL"
    )
    S3_REGION_NAME: Optional[str] = Field(default="ru-1", env="S3_REGION_NAME")

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )


configs = Configs()


def get_db_url():
    return (
        f"postgresql+asyncpg://{configs.DB_USER}:{configs.DB_PASS}@"
        f"{configs.DB_HOST}:{configs.DB_PORT}/{configs.DB_NAME}"
    )


def get_auth_data():
    return {"secret_key": configs.SECRET_KEY, "algorithm": configs.ALGORITHM}


