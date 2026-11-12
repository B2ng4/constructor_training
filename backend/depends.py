from typing import Optional

import boto3
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import configs
from core.database import get_async_session
from models.users import User, UserRole
from repositories.actions_repository import ActionsRepository
from repositories.courses_repository import CoursesRepository
from repositories.levels_repository import LevelsRepository
from repositories.tags_repository import TagsRepository
from repositories.trainings_repository import TrainingRepository
from repositories.users_repository import UserRepository
from services.courses_service import CoursesService
from services.external_services.gigachat_tts_service import GigaChatTTSService
from services.external_services.s3_service import S3Service
from services.pdf_ai_service import PdfAiService
from services.organizations_service import OrganizationsService
from services.temp_employee_accounts_service import (
    TempEmployeeAccountsService,
    is_account_expired,
)
from services.trainings_service import TrainingsService
from services.user_service import UserService

from services.video_ai_service import VideoAIService

"""
Файл внедрения зависимостей
"""

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="auth/login", auto_error=False
)


async def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> UserRepository:
    """Получение репозитория пользователей"""
    return UserRepository(session)


async def get_trainings_repository(
    session: AsyncSession = Depends(get_async_session),
) -> TrainingRepository:
    """Получение репозитория тренингов"""
    return TrainingRepository(session)


async def get_tags_repository(
    session: AsyncSession = Depends(get_async_session),
) -> TagsRepository:
    """Получение репозитория тегов"""
    return TagsRepository(session)


async def get_levels_repository(
    session: AsyncSession = Depends(get_async_session),
) -> LevelsRepository:
    """Получение репозитория уровней"""
    return LevelsRepository(session)


async def get_actions_repository(
    session: AsyncSession = Depends(get_async_session),
) -> ActionsRepository:
    """Получение ипов действий"""
    return ActionsRepository(session)


async def get_courses_repository(
    session: AsyncSession = Depends(get_async_session),
) -> CoursesRepository:
    """Получение репозитория курсов"""
    return CoursesRepository(session)


async def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    """Получение сервиса пользователей"""
    repo = UserRepository(session)
    return UserService(repo, session)


async def get_trainings_service(
    session: AsyncSession = Depends(get_async_session),
) -> TrainingsService:
    """Получение сервиса тренингов"""
    return TrainingsService(session)


async def get_courses_service(
    session: AsyncSession = Depends(get_async_session),
) -> CoursesService:
    """Получение сервиса курсов"""
    return CoursesService(session)


async def get_organizations_service(
    session: AsyncSession = Depends(get_async_session),
) -> OrganizationsService:
    return OrganizationsService(session)


async def get_s3_service(
    session: AsyncSession = Depends(get_async_session),
) -> S3Service:
    """Получение S3 сервиса"""
    return S3Service(session)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Получение текущего аутентифицированного пользователя

    Декодирует JWT токен и возвращает объект пользователя из БД
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])
        user_identifier: str = payload.get("sub")
        if user_identifier is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = None
    if user_identifier.isdigit():
        user = await user_repo.get_by_id(int(user_identifier))
    if user is None:
        user = await user_repo.find_one_or_none(user_identifier)

    if user is None:
        raise credentials_exception

    if is_account_expired(user.expires_at):
        await TempEmployeeAccountsService(session).cleanup_user_if_expired(user)
        raise credentials_exception

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    user_repo: UserRepository = Depends(get_user_repository),
) -> Optional[User]:
    """То же, что get_current_user, но без ошибки: None, если нет/невалидный токен."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])
        user_identifier: str = payload.get("sub")
        if not user_identifier:
            return None
    except JWTError:
        return None
    user = None
    if user_identifier.isdigit():
        user = await user_repo.get_by_id(int(user_identifier))
    if user is None:
        user = await user_repo.find_one_or_none(user_identifier)
    return user


async def get_current_creator(
    user: User = Depends(get_current_user),
) -> User:
    if user.role == UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для создателей тренингов",
        )
    return user


def get_video_ai_service() -> VideoAIService:
    return VideoAIService()


def get_pdf_ai_service() -> PdfAiService:
    return PdfAiService()


def get_gigachat_tts_service() -> GigaChatTTSService:
    return GigaChatTTSService()
