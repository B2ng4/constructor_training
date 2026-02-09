# schemas/levels.py
from pydantic import BaseModel, Field
from typing import Optional


class LevelBase(BaseModel):
    """Базовая схема уровня"""

    label: str = Field(..., description="Название уровня")


class LevelCreate(LevelBase):
    """Схема для создания уровня"""

    pass  # Наследует label от LevelBase


class LevelUpdate(BaseModel):
    """Схема для обновления уровня"""

    label: Optional[str] = Field(None, description="Новое название уровня")


class LevelResponse(LevelBase):
    """Схема ответа"""

    value: int

    class Config:
        from_attributes = True
