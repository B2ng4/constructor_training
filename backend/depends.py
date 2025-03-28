from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from models.users import User
from repositories.users_repository import UserRepository
from repositories.trainings_repository import TrainingRepository
from services.user_service import UserService
from  services.mail_service import EmailService
from  services.trainings_service import TrainingsService

"""
Файл внедрения зависимостей
"""
# Для пользователей (асинхронная версия)
async def get_user_service(
    session: AsyncSession = Depends(get_async_session)) -> UserService:
    repo = UserRepository(session)
    email_service = EmailService()
    return UserService(repo, email_service)


async def get_trainings_service(
    session: AsyncSession = Depends(get_async_session)) -> TrainingsService:
    repo = TrainingRepository(session)
    return TrainingsService(repo)

