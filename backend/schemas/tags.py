# schemas/tags.py
from typing import Optional

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    label: str = Field(..., min_length=1, max_length=50, description="Название тега")


class TagCreate(TagBase):
    """Схема для создания тега"""

    pass


class TagUpdate(BaseModel):
    """Схема для обновления тега"""

    label: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Новое название тега"
    )


class TagResponse(TagBase):
    """Схема ответа с тегом"""

    value: int

    class Config:
        from_attributes = True


class TagWithTrainingsCount(TagResponse):
    """Схема тега с количеством тренингов"""

    trainings_count: int = Field(0, description="Количество тренингов с этим тегом")
