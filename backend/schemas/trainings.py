from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4, Field
from uuid import UUID


class TypesActionBase(BaseModel):
    name: Optional[str] = None


class TypesActionResponse(TypesActionBase):
    id: int

    class Config:
        from_attributes = True


class ImageBase(BaseModel):
    url: str


class ImageResponse(ImageBase):
    uuid: UUID4

    class Config:
        from_attributes = True


class TrainingStepBase(BaseModel):
    step_number: int
    action_type_id: Optional[int] = None
    area: Optional[Dict[str, int]] = None
    meta: Optional[Dict[str, Any]] = None
    annotation: Optional[str] = None
    image: Optional[UUID4] = None


class TrainingStepCreate(TrainingStepBase):
    pass


class TrainingStepResponse(TrainingStepBase):
    id: int
    training_id: int
    action_type: Optional[TypesActionResponse] = None
    image_details: Optional[ImageResponse] = None

    class Config:
        from_attributes = True


class TrainingBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    cover_image_uuid: Optional[UUID4] = None


class TrainingCreate(TrainingBase):
    steps: List[TrainingStepCreate] = None


class TrainingUpdate(TrainingBase):
    end_date: Optional[datetime] = None
    type_id: Optional[int] = None


class TrainingAssignmentCreate(BaseModel):
    user_ids: List[int] = Field(..., min_items=1)


class TrainingAssignmentUpdate(BaseModel):
    completed: bool


class TrainingAssignmentResponse(BaseModel):
    id: int
    user_id: int
    assigned_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrainingResponse(TrainingBase):
    id: int
    creator_id: int
    created_at: datetime
    type_id: Optional[int] = None
    steps: List[TrainingStepResponse] = []

    class Config:
        from_attributes = True


class TrainingDetailResponse(TrainingResponse):
    assignments: List[TrainingAssignmentResponse] = []
    type_name: Optional[str] = None
    type_data: Optional[Dict[str, Any]] = None
