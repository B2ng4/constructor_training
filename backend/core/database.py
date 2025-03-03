from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr
from core.config import get_db_url
from sqlalchemy import text
import asyncio


DATABASE_URL = get_db_url()

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL)

# Создаем фабрику асинхронных сессий
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

# Зависимость для получения асинхронной сессии
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session



