from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, UUID4, Field, field_validator
from uuid import UUID


# === Модели для TypesAction ===
class ActionTypeResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# === Модели для Tags ===
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True


# === Модели для Levels ===
class LevelBase(BaseModel):
    name: str


class LevelCreate(LevelBase):
    pass


class LevelResponse(LevelBase):
    id: int

    class Config:
        from_attributes = True


# === Модели для TrainingStep ===
class TrainingStepBase(BaseModel):
    step_number: int
    action_type_id: Optional[int] = None
    training_uuid: Optional[UUID4] = None
    area: Optional[Dict[str, int]] = None
    meta: Optional[Dict[str, Any]] = None
    annotation: Optional[str] = None
    image_url: Optional[str] = None


class TrainingStepCreate(TrainingStepBase):
    pass


class TrainingStepUpdate(BaseModel):
    id: Optional[int] = None
    step_number: Optional[int] = None
    action_type_id: Optional[int] = None
    area: Optional[Dict[str, int]] = None
    meta: Optional[Dict[str, Any]] = None
    annotation: Optional[str] = None
    image_url: Optional[str] = None


class TrainingStepResponse(TrainingStepBase):
    id: int
    action_type: Optional[ActionTypeResponse] = None

    class Config:
        from_attributes = True



# === Модели для Training ===
class TrainingBase(BaseModel):
    title: str
    description: str
    level_id: Optional[int] = None
    duration_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Ожидаемое время прохождения тренинга в минутах"
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
    steps: Optional[List[Union[TrainingStepCreate, TrainingStepUpdate]]] = Field(default_factory=list)
    tag_ids: Optional[List[int]] = None

    class Config:
        from_attributes = True


class TrainingResponse(BaseModel):
    uuid: UUID4
    title: str
    description: str
    creator_id: int
    level_id: Optional[int] = None
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime] = None

    # Nested relationships
    level: Optional[LevelResponse] = None
    tags: List[TagResponse] = Field(default_factory=list)
    steps: List[TrainingStepResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class TrainingListResponse(BaseModel):
    """
    Упрощенная модель для списка тренингов
    """
    uuid: UUID4
    title: str
    description: str
    creator_id: int
    level_id: Optional[int] = None
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime] = None
    level: Optional[LevelResponse] = None
    tags: List[TagResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
