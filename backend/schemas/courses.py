from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field

from schemas.levels import LevelResponse


class CourseTrainingItemResponse(BaseModel):
    uuid: UUID4
    title: str
    description: str
    publish: bool = False
    duration_minutes: Optional[int] = None
    level: Optional[LevelResponse] = None

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    training_uuids: List[UUID4] = Field(default_factory=list)


class CourseListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    creator_id: int
    created_at: Optional[datetime] = None
    trainings: List[CourseTrainingItemResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
