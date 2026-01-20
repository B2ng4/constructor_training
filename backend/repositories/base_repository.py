# repositories/base_repository.py
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий с CRUD операциями
    """

    def __init__(
            self,
            model: Type[ModelType],
            session: AsyncSession,
            pk_field: str = "id"
    ):
        self.model = model
        self.session = session
        self.pk_field = pk_field

    def _get_pk_column(self):
        """Получить колонку первичного ключа"""
        return getattr(self.model, self.pk_field)

    async def create(self, **kwargs) -> ModelType:
        """Создание записи"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получение записи по ID (или любому PK полю)"""
        return await self.session.get(self.model, id)

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None
    ) -> List[ModelType]:
        """Получение всех записей"""
        query = select(self.model).offset(skip).limit(limit)

        if order_by:
            order_column = getattr(self.model, order_by, None)
            if order_column is not None:
                query = query.order_by(order_column)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Обновление записи"""
        pk_column = self._get_pk_column()

        query = (
            update(self.model)
            .where(pk_column == id)
            .values(**kwargs)
        )

        result = await self.session.execute(query)
        await self.session.commit()

        if result.rowcount > 0:
            return await self.get_by_id(id)
        return None

    async def delete(self, id: int) -> bool:
        """Удаление записи"""
        pk_column = self._get_pk_column()

        query = delete(self.model).where(pk_column == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def exists(self, id: int) -> bool:
        """Проверка существования записи"""
        result = await self.get_by_id(id)
        return result is not None

    async def count(self) -> int:
        """Подсчет количества записей"""
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar()
