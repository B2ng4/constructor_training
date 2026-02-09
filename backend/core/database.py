from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncAttrs,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr
from core.config import get_db_url
from sqlalchemy import MetaData
import asyncio

DATABASE_URL = get_db_url()
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session
