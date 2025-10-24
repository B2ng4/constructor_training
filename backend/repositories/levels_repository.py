# repositories/levels_repository.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.trainings import Levels
from repositories.base_repository import BaseRepository


class LevelsRepository(BaseRepository[Levels]):
    """
    Репозиторий для работы с уровнями
    """

    def __init__(self, session: AsyncSession):
        super().__init__(model=Levels, session=session, pk_field="value")

    async def get_by_label(self, label: str) -> Optional[Levels]:
        """Получение уровня по названию"""
        from sqlalchemy import select

        query = select(Levels).where(Levels.label == label)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
