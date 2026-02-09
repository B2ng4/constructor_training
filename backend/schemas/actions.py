# schemas/actions.py

from pydantic import BaseModel
from typing import Optional, Dict, Any


class ActionBase(BaseModel):
    """
    Базовая схема, содержащая общие поля для создания и ответа.
    """

    type: Optional[str]
    name: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class ActionCreate(ActionBase):
    """
    Схема для создания нового действия.
    Наследует все поля от ActionBase.
    """

    pass


class ActionUpdate(BaseModel):
    """
    Схема для частичного обновления действия (PATCH).
    Все поля опциональны.
    """

    type: Optional[str] = None
    name: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class ActionResponse(ActionBase):
    """
    Схема для ответа API.
    Представляет полный объект из базы данных, включая id.
    """

    id: int

    class Config:
        from_attributes = True
