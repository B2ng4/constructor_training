from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os


class Configs(BaseSettings):
    #Для инициализации проекта#
    PROJECT_NAME:str = "EventsKnastu"
    PROJECT_DESCRIPTION:str = "Проект для создания мероприятий в Кнагу"

    #Для аутенфикации
    SECRET_KEY: str = Field(default="your-secret-key", env="SECRET_KEY")  # Секретный ключ для JWT и шифрования
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")  # Алгоритм шифрования для JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # Время жизни токена

    # Настройки БД
    DB_HOST: Optional[str] = Field(default="localhost", env="DB_HOST")
    DB_PORT: Optional[int] = Field(default=5432, env="DB_PORT")
    DB_USER: Optional[str] = Field(default="postgres", env="DB_USER")
    DB_NAME: Optional[str] = Field(default="timofeymac", env="DB_NAME")
    DB_PASS: Optional[str] = Field(default="admin", env="DB_PASS")

    # Настройки почты
    MAIL_USERNAME: Optional[str] = Field(default="timsidorin@gmail.com", env="MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = Field(default="xdfj qlia vmpy gskl", env="MAIL_PASSWORD")
    MAIL_FROM: Optional[str] = Field(default="timsidorin@gmail.com", env="MAIL_FROM")
    MAIL_PORT: Optional[int] = Field(default=587, env="MAIL_PORT")
    MAIL_SERVER: Optional[str] = Field(default="smtp.gmail.com", env="MAIL_SERVER")
    MAIL_STARTTLS: bool = Field(default=True, env="MAIL_STARTTLS")
    MAIL_SSL_TLS: bool = Field(default=False, env="MAIL_SSL_TLS")


    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )




configs = Configs()
def get_db_url():
    return (f"postgresql+asyncpg://{configs.DB_USER}:{configs.DB_PASS}@"
            f"{configs.DB_HOST}:{configs.DB_PORT}/{configs.DB_NAME}")


def get_auth_data():
    return {"secret_key": configs.SECRET_KEY, "algorithm": configs.ALGORITHM}


