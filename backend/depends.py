from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_async_session
from backend.models.users import User
from backend.repositories.users import UserRepository
from backend.services.users import UserService
from repositories.books import BookRepository
from services.books import  BookService

"""
Файл внедрения зависимостей
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.books import BookRepository
from backend.repositories.users import UserRepository
from backend.services.books import BookService
from backend.services.users import UserService
from backend.core.database import get_async_session



# Для книг (если используется синхронная сессия)
def get_book_service(session: AsyncSession = Depends(get_async_session)) -> BookService:
    repo = BookRepository(session)
    return BookService(repo)

# Для пользователей (асинхронная версия)
async def get_user_service(
    session: AsyncSession = Depends(get_async_session)) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)



