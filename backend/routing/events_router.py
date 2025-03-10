
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from depends import get_events_service
from starlette import status
from services.events_service import EventsService

from schemas.events import EventResponse, EventUpdate, EventCreate

router = APIRouter(prefix="/event", tags=["Мероприятия"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/create")

async def create_event(ser_data: EventCreate,
                       token: str = Depends(oauth2_scheme),
                       event_service: EventsService = Depends(get_events_service)):
    """Создание нового мероприятия (только админы и суперпользователи"""
    if await event_service.create_event(ser_data):
        return HTTPException(status.HTTP_200_OK, detail="Мероприятие успешно создано")
    else:
        return HTTPException(status_code=404, detail="Мероприятие не создано")


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int,service: EventsService = Depends(get_events_service)):
    event = await service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    return event


@router.put("/{event_id}")
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    service: EventsService = Depends(get_events_service)):
    event = await service.update_event(event_id, event_data)
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    return HTTPException(status_code=200, detail="Данные мероприятия успешно обновлены")


@router.delete("/{event_id}")
async def delete_event(event_id: int, service: EventsService = Depends(get_events_service)):
    if await service.delete_event(event_id):
        return HTTPException(status.HTTP_200_OK, detail="Мероприятие успешно удалено")
    else:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
