# schemas/levels.py
from pydantic import BaseModel, Field
from typing import Optional


class ActionBase(BaseModel):
    """Базовая схема Действия"""
    label: str = Field(..., description="Название действия")


class ActionCreate(ActionBase):
    """Схема для создания действия"""
    pass


class ActionUpdate(BaseModel):
    """Схема для обновления уровня"""
    label: Optional[str] = Field(None, description="Новое название действия")


class ActionResponse(ActionBase):
    """Схема ответа"""
    value: int
    class Config:
        from_attributes = True
