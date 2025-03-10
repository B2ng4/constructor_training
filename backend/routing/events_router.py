
from fastapi import APIRouter, Depends, HTTPException

from schemas.events import EventCreate
from fastapi.security import OAuth2PasswordBearer
from depends import get_events_service

from services.events_service import EventsService

router = APIRouter(prefix="/event", tags=["Мероприятия"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/create")

async def create_event(ser_data: EventCreate,
                       token: str = Depends(oauth2_scheme),
                       event_service: EventsService = Depends(get_events_service)):
    """Создание нового мероприятия (только админы и суперпользователи"""
    return await event_service.create_event(ser_data)
