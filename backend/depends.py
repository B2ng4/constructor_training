import boto3
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_session
from models.users import User
from repositories.users_repository import UserRepository
from repositories.trainings_repository import TrainingRepository
from services.user_service import UserService
from services.external_services.mail_service import EmailService
# from services.external_services.redis_service import RedisService
from services.trainings_service import TrainingsService
from core.config import configs, Configs
from services.external_services.s3_service import S3Service
# import aioredis
"""
Файл внедрения зависимостей
"""


# Для пользователей (асинхронная версия)
async def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    repo = UserRepository(session)
    email_service = EmailService()
    return UserService(repo, email_service)


async def get_trainings_service(
    session: AsyncSession = Depends(get_async_session),
) -> TrainingsService:
    return TrainingsService(session)


def get_s3_service() -> S3Service:
    return S3Service()

#
# async def get_redis_service() -> aioredis.Redis:
#     return await RedisService.connect()


