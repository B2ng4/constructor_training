from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4
from uuid import UUID






class TrainingBase(BaseModel):
    """Базовый тренинг"""
    title: str
    description: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    cover_image_uuid: Optional[UUID4] = None



class TrainingStepBase(BaseModel):
    """Шаг Тренинга"""
    step_number: int
    image_url: str
    area: Dict[str, int]
    description: str


class TrainingStepCreate(TrainingStepBase):
    pass



class TrainingCreate(TrainingBase):
    """Создание тренига (добавление шагов и типа тренинга)"""
    steps: List[TrainingStepCreate]
    type_id: Optional[int] = None


class TrainingUpdate(BaseModel):
    """Обновление тренига (Обновление  шагов и типа тренинга)"""
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    cover_image_uuid: Optional[UUID4] = None
    type_id: Optional[int] = None




class TrainingStepResponse(TrainingStepBase):
    id: int
    training_id: int

    class Config:
        from_attributes = True



# Модели для назначения тренингов
class TrainingAssignmentCreate(BaseModel):
    user_ids: List[int]

class TrainingAssignmentUpdate(BaseModel):
    completed: bool



class TrainingResponse(TrainingBase):
    id: int
    creator_id: int
    created_at: datetime
    type_id: Optional[int] = None
    steps: List[TrainingStepResponse]

    class Config:
        from_attributes = True



class TrainingAssignmentResponse(BaseModel):
    id: int
    user_id: int
    assigned_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrainingDetailResponse(TrainingResponse):
    assignments: List[TrainingAssignmentResponse]
    type_name: Optional[str] = None
    type_data: Optional[Dict[str, Any]] = None














