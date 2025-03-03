from datetime import datetime

from sqlalchemy import Column, Integer
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa
from core.database import *




class Book(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(100))
    annotation: Mapped[str] = mapped_column(sa.Text)
    date_publishing: Mapped[datetime] = mapped_column(sa.DateTime)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())