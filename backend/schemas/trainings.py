from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4, Field
from uuid import UUID




class ActionTypeResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True



class ImageResponse(BaseModel):
    uuid: UUID4
    url: str
    class Config:
        from_attributes = True


class TrainingStepBase(BaseModel):
    step_number: int
    action_type_id: Optional[int] = None
    training_id: Optional[int] = None
    area: Optional[Dict[str, int]] = None
    meta: Optional[Dict[str, Any]] = None
    annotation: Optional[str] = None
    image_uuid: Optional[UUID4] = None


class TrainingStepCreate(TrainingStepBase):
    pass


class TrainingStepResponse(TrainingStepBase):
    action_type: ActionTypeResponse
    image: ImageResponse
    class Config:
        from_attributes = True
        exclude = {"action_type_id", "image_uuid"}


class TrainingBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    cover_image: Optional[UUID4] = None


class TrainingCreate(TrainingBase):
    steps: List[TrainingStepCreate] = None


class TrainingUpdate(TrainingBase):
    end_date: Optional[datetime] = None
    type_id: Optional[int] = None


class TrainingResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    creator_id: int
    created_at: datetime
    cover_image: Optional[UUID4] = None
    steps: List[TrainingStepResponse]

    class Config:
        from_attributes = True




