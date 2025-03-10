
from fastapi import APIRouter, Depends, HTTPException

from schemas.events import EventCreate

router = APIRouter(prefix="/event", tags=["Мероприятия"])



@router.post("/create")
async def create_event(user_data: EventCreate):
    pass
