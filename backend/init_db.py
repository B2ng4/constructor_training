"""
Инициализация БД при первом запуске контейнера.

Ждёт готовности PostgreSQL и создаёт все таблицы по моделям
(Base.metadata.create_all — идемпотентно, существующие таблицы не трогает).
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine

from core.database import DATABASE_URL, Base
from models import courses, organizations, tasks, trainings, users  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(levelname)s [init_db] %(message)s")
logger = logging.getLogger("init_db")

RETRIES = 30
DELAY = 2


async def init() -> None:
    engine = create_async_engine(DATABASE_URL)
    try:
        for attempt in range(1, RETRIES + 1):
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("Таблицы созданы (или уже существовали)")
                return
            except Exception as exc:
                logger.warning(
                    "БД недоступна (попытка %s/%s): %s", attempt, RETRIES, exc
                )
                if attempt == RETRIES:
                    raise
                await asyncio.sleep(DELAY)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init())
