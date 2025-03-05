from fastapi import HTTPException, status, BackgroundTasks
from os import access
from typing import List, Optional

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import EmailStr
from schemas.users import UserRegister, UserLogin, User
from repositories.users import UserRepository
from utils.security import verify_password, get_password_hash, create_access_token
from backend.schemas import mail
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import configs

from backend.schemas.mail import mail_send
from backend.services.mail import EmailService


class UserService:
    def __init__(self, repo: UserRepository, email_service: EmailService):
        self.user_repo = repo
        self.email_service = email_service

    async def register(self, user_data: UserRegister) -> bool:
        mail = mail_send(email = user_data.email, subject="Добро пожаловать в EventsKnastu!", body="Добро пожаловать в EventsKnastu!")
        BackgroundTasks.add_task(self.email_service.send_email, mail)
        return await self.user_repo.add_user(user_data)


    async def authenticate(self, email: EmailStr, password: str):
        user = await self.user_repo.find_one_or_none(email=email)
        if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
            return None
        return user


    async def login(self, credential: UserLogin) -> Optional[str]:
        # Используем authenticate_user для проверки email и пароля
        user = await self.authenticate(email=credential.username, password=credential.password)
        if not user:
            return None

        access_token = create_access_token(
            data={"sub": user.email},
        )
        return access_token


    async def get_current_user(self, token: str) -> User:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])
        email: str = payload.get("sub")

        user = await self.user_repo.find_one_or_none(email=email)
        if user is None:
            return None
        return User.from_orm(user)



