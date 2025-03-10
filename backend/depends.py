from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from models.users import User
from repositories.users_repository import UserRepository
from services.user_service import UserService
from  services.mail_service import EmailService
from  services.events_service import EventsService

"""
Файл внедрения зависимостей
"""
# Для пользователей (асинхронная версия)
async def get_user_service(
    session: AsyncSession = Depends(get_async_session)) -> UserService:
    repo = UserRepository(session)
    email_service = EmailService()
    return UserService(repo, email_service)

async def get_events_service(
    session: AsyncSession = Depends(get_async_session)) -> EventsService:
    repo = UserRepository(session)
    return EventsService(repo)

