from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, UUID4, Field
from uuid import UUID


class ActionTypeResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


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


class TrainingStepResponse(TrainingStepBase):
    id: int
    action_type: Optional[ActionTypeResponse] = None

    class Config:
        from_attributes = True
        exclude = {"action_type_id"}


class TrainingBase(BaseModel):
    title: str
    description: str
    created_at: Optional[datetime] = None


class TrainingCreate(TrainingBase):
    steps: Optional[List[TrainingStepCreate]] = Field(default_factory=list)


class TrainingStepUpdate(BaseModel):
    step_number: Optional[int] = None
    action_type_id: Optional[int] = None
    area: Optional[Dict[str, int]] = None
    meta: Optional[Dict[str, Any]] = None
    annotation: Optional[str] = None
    image_url: Optional[str] = None


class TrainingResponse(BaseModel):
    uuid: UUID4
    title: str
    description: str
    creator_id: int
    created_at: datetime = None
    steps: List[TrainingStepResponse] = None

    class Config:
        from_attributes = True


class TrainingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    end_date: Optional[datetime] = None
    type_id: Optional[int] = None
    steps: Optional[List[Union[TrainingStepCreate, TrainingStepUpdate]]] = Field(default_factory=list)

    class Config:
        from_attributes = True
