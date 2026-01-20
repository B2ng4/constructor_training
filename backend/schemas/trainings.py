from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, UUID4, Field, field_validator
from uuid import UUID

from schemas.actions import ActionTypeResponse
from schemas.levels import LevelResponse
from schemas.tags import TagResponse


# === Модели для TrainingStep ===

class TrainingStepBase(BaseModel):
    step_number: int
    action_type_id: Optional[int] = None
    training_uuid: Optional[UUID4] = None
    parent_step_id: Optional[int] = None
    area: Optional[Dict[str, int]] = None
    meta: Optional[Dict[str, Any]] = None
    annotation: Optional[str] = None
    image_url: Optional[str] = None


class TrainingStepCreate(TrainingStepBase):
    steps: Optional[List['TrainingStepCreate']] = Field(default_factory=list)


class TrainingStepUpdate(BaseModel):
    id: Optional[int] = None
    step_number: Optional[int] = None
    action_type_id: Optional[int] = None
    parent_step_id: Optional[int] = None
    area: Optional[Dict[str, int]] = None
    meta: Optional[Dict[str, Any]] = None
    annotation: Optional[str] = None
    image_url: Optional[str] = None
    steps: Optional[List[Union['TrainingStepCreate', 'TrainingStepUpdate']]] = Field(default_factory=list)


class TrainingStepResponse(TrainingStepBase):
    id: int
    action_type: Optional[ActionTypeResponse] = None

    class Config:
        from_attributes = True


TrainingStepCreate.model_rebuild()
TrainingStepUpdate.model_rebuild()


class TrainingBase(BaseModel):
    title: str
    description: str
    level_id: Optional[int] = None
    duration_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Ожидаемое время прохождения тренинга в минутах"
    )

    publish: bool = Field(
        default=False,
        description="Опубликован ли тренинг"
    )

    skip_steps: Optional[bool] = Field(
        default=True,
        description="Пропускать шаги?"
    )

    @field_validator('duration_minutes')
    @classmethod
    def validate_duration(cls, v):
        if v is not None and v < 0:
            raise ValueError('Время прохождения не может быть отрицательным')
        return v


class TrainingCreate(TrainingBase):
    steps: Optional[List[TrainingStepCreate]] = Field(default_factory=list)
    tag_ids: Optional[List[int]] = Field(default_factory=list)


class TrainingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    level_id: Optional[int] = None
    duration_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Ожидаемое время прохождения тренинга в минутах"
    )
    publish: Optional[bool] = Field(
        None,
        description="Опубликован ли тренинг"
    )
    tag_ids: Optional[List[int]] = None

    class Config:
        from_attributes = True


class TrainingListResponse(BaseModel):
    """
    Упрощенная модель для списка тренингов (БЕЗ шагов)
    """
    uuid: UUID4
    title: str
    description: str
    creator_id: int
    level_id: Optional[int] = None
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime] = None
    publish: bool = False
    skip_steps: Optional[bool] = None
    level: Optional[LevelResponse] = None
    tags: List[TagResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class TrainingResponse(BaseModel):
    """
    Полная модель тренинга с шагами (БЕЗ вложенных подшагов в response)
    Вложенные подшаги загружаются через GET /training/{uuid}/steps
    """

    uuid: UUID4
    title: str
    description: str
    creator_id: int
    level_id: Optional[int] = None
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime] = None
    publish: bool = False
    skip_steps: Optional[bool] = None
    level: Optional[LevelResponse] = None
    tags: List[TagResponse] = Field(default_factory=list)
    steps: List[TrainingStepResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True




class TrainingStepResponseWithId(TrainingStepResponse):
    """Ответ с ID шага для операций обновления"""
    pass


class StepBulkCreateRequest(BaseModel):
    """Запрос для массового создания шагов"""
    steps: List[TrainingStepCreate]


class StepBulkUpdateRequest(BaseModel):
    """Запрос для массового обновления шагов"""
    steps: List[TrainingStepUpdate]
