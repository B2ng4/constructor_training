from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class EventCreate(BaseModel):
    title: str
    type_id: int
    start_date: datetime
    end_date: Optional[datetime] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    type_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class EventResponse(BaseModel):
    id: int
    title: str
    type_id: int
    start_date: datetime
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventDetailResponse(EventResponse):
    type_name: str
    type_data: Optional[Dict[str, Any]] = None