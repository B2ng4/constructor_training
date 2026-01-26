# repositories/levels_repository.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.trainings import TypesAction
from repositories.base_repository import BaseRepository


class ActionsRepository(BaseRepository[TypesAction]):
    """
    Репозиторий для работы с действиями
    """

    def __init__(self, session: AsyncSession):
        super().__init__(model=TypesAction, session=session, pk_field="id")

    async def get_by_id(self, id: str) -> Optional[TypesAction]:
        """Получение действия по названию"""
        from sqlalchemy import select

        query = select(TypesAction).where(TypesAction.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
