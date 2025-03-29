import string
import random

import httpx
from fastapi import HTTPException, status, BackgroundTasks
from os import access
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import EmailStr
from schemas.users import UserRegister, UserLogin, User
from repositories.users_repository import UserRepository
from utils.security import verify_password, get_password_hash, create_access_token
from schemas import mail
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import configs
from schemas.mail import mail_send
from services.mail_service import EmailService
from utils.security import create_access_token


class UserService:
    def __init__(self, repo: UserRepository, email_service: EmailService):
        self.user_repo = repo
        self.email_service = email_service

    async def register(self, user_data: UserRegister, background_tasks: BackgroundTasks) -> bool:
        mail = mail_send(email = user_data.email,
                         subject=f"Добро пожаловать в {configs.PROJECT_NAME}!",
                         body=f"Вы успешно зарегистрированы в {configs.PROJECT_NAME}!")
        background_tasks.add_task(self.email_service.send_email, mail)
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
        return User.model_validate(user)



    async def get_yandex_access_token(self, code: str) -> str:
        """
        Получает access token от Яндекса, используя authorization code.
        """
        url = "https://oauth.yandex.com/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": configs.YANDEX_CLIENT_ID,
            "client_secret": configs.YANDEX_CLIENT_SECRET,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка при получении токена от Яндекса: {response.text}"
                )
            result = response.json()
            access_token = result.get("access_token")
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не удалось получить access token от Яндекса"
                )
            return access_token


    async def get_yandex_user_info(self, access_token: str) -> dict:
        """
        Получает информацию о пользователе от Яндекса по access token.
        """
        url = "https://login.yandex.ru/info"
        headers = {"Authorization": f"OAuth {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка при получении данных пользователя от Яндекса: {response.text}"
                )
            return response.json()

    async def get_or_create_user_from_yandex(self, yandex_user: dict) -> User:
        email = yandex_user.get("default_email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yandex user email not found"
            )
        user_in_db = await self.user_repo.find_one_or_none(email=email)
        if user_in_db:
            return User.model_validate(user_in_db)
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        hashed_password = get_password_hash(random_password)
        new_user_data = UserRegister(
            email=email,
            password=hashed_password,
            last_name=yandex_user.get("last_name"),
            first_name=yandex_user.get("first_name"),
            phone_number="+79249194507",
            role_id= 1
        )
        added = await self.user_repo.add_user(new_user_data)
        if not added:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать пользователя"
            )
        user_in_db = await self.user_repo.find_one_or_none(email=email)
        if not user_in_db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Пользователь не найден после создания"
            )
        return User.model_validate(user_in_db)

    async def create_access_token_by_yandex(self, user:User) -> Optional[str]:

        access_token = create_access_token(
            data={"sub": user.email},
        )
        return access_token

