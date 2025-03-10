
from fastapi import APIRouter, Depends, HTTPException

from schemas.events import EventCreate
from fastapi.security import OAuth2PasswordBearer


router = APIRouter(prefix="/event", tags=["Мероприятия"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/create")

async def create_event(ser_data: EventCreate,token: str = Depends(oauth2_scheme)):
    """Создание нового мероприятия (только админы и суперпользователи"""
    pass
