from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID

class EventCreate(BaseModel):
    title: str
    type_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    image_uuid: Optional[UUID] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    type_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    image_uuid: Optional[UUID] = None


class EventResponse(BaseModel):
    id: int
    title: str
    type_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    image_uuid: Optional[UUID] = None

    class Config:
        from_attributes = True


class EventDetailResponse(EventResponse):
    type_name: str
    type_data: Optional[Dict[str, Any]] = None
    image_uuid: Optional[UUID] = None