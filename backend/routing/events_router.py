
from fastapi import APIRouter, Depends, HTTPException

from schemas.events import event_create

router = APIRouter(prefix="/event", tags=["Мероприятия"])



@router.post("/create")
async def create_event(user_data: event_create):
    pass
