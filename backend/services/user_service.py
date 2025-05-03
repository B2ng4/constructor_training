import string
import random

import httpx
from fastapi import HTTPException, status, BackgroundTasks
from os import access
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import EmailStr
from schemas.users import UserRegister, UserLogin, User, UserResponse
from repositories.users_repository import UserRepository
from utils.security import verify_password, get_password_hash, create_access_token
from schemas import mail
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import configs
from schemas.mail import mail_send
from services.external_services.mail_service import EmailService
from utils.security import create_access_token, decode_access_token


class UserService:
    def __init__(self, repo: UserRepository, email_service: EmailService):
        self.user_repo = repo
        self.email_service = email_service

    async def register(
        self, user_data: UserRegister, background_tasks: BackgroundTasks
    ) -> bool:
        mail = mail_send(
            email=user_data.email,
            subject=f"Добро пожаловать в {configs.PROJECT_NAME}!",
            body=f"Вы успешно зарегистрированы в {configs.PROJECT_NAME}!",
        )
        background_tasks.add_task(self.email_service.send_email, mail)
        return await self.user_repo.add_user(user_data)

    async def authenticate(self, email: EmailStr, password: str):
        user = await self.user_repo.find_one_or_none(email=email)
        if (
            not user
            or verify_password(plain_password=password, hashed_password=user.password)
            is False
        ):
            return None
        return user

    async def login(self, credential: UserLogin) -> Optional[str]:
        # Используем authenticate_user для проверки email и пароля
        user = await self.authenticate(
            email=credential.username, password=credential.password
        )
        if not user:
            return None

        access_token = create_access_token(
            data={"sub": user.email},
        )
        return access_token

    async def get_current_user(self, token: str) -> UserResponse:
        payload = decode_access_token(token=token)
        email: str = payload.get("sub")

        user = await self.user_repo.find_one_or_none(email=email)
        if user is None:
            return None
        return UserResponse.model_validate(user)
