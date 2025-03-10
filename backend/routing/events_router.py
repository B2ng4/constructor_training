
from fastapi import APIRouter, Depends, HTTPException

from schemas.events import Event_create

router = APIRouter(prefix="/event", tags=["Мероприятия"])



@router.post("/create")
async def create_event(user_data: Event_create):
    pass
