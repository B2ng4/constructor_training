from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from models.users import User
from repositories.users import UserRepository
from services.users import UserService
from repositories.books import BookRepository
from services.books import  BookService
from  services.mail import EmailService

"""
Файл внедрения зависимостей
"""

# Для книг (если используется синхронная сессия)
def get_book_service(session: AsyncSession = Depends(get_async_session)) -> BookService:
    repo = BookRepository(session)
    return BookService(repo)

# Для пользователей (асинхронная версия)
async def get_user_service(
    session: AsyncSession = Depends(get_async_session)) -> UserService:
    repo = UserRepository(session)
    email_service = EmailService
    return UserService(repo, email_service)



