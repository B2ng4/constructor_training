# repositories/tags_repository.py
from typing import List, Optional
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.trainings import Tags, Training, training_tags


class TagsRepository:
    """
    Репозиторий для работы с тегами
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, label: str) -> Tags:
        """Создание тега"""
        tag = Tags(label=label)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def get_by_id(self, value: int) -> Optional[Tags]:
        """Получение тега по value (ID)"""
        return await self.session.get(Tags, value)

    async def get_by_name(self, label: str) -> Optional[Tags]:
        """Получение тега по label (имени)"""
        query = select(Tags).where(Tags.label == label)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: str = "label"
    ) -> List[Tags]:
        """Получение всех тегов"""
        query = select(Tags).offset(skip).limit(limit)

        if order_by:
            order_column = getattr(Tags, order_by, None)
            if order_column is not None:
                query = query.order_by(order_column)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, value: int, label: str) -> Optional[Tags]:
        """Обновление тега"""
        query = (
            update(Tags)
            .where(Tags.value == value)
            .values(label=label)
        )
        result = await self.session.execute(query)
        await self.session.commit()

        if result.rowcount > 0:
            return await self.get_by_id(value)
        return None

    async def delete(self, value: int) -> bool:
        """Удаление тега"""
        query = delete(Tags).where(Tags.value == value)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def exists(self, value: int) -> bool:
        """Проверка существования тега"""
        tag = await self.get_by_id(value)
        return tag is not None

    async def count(self) -> int:
        """Подсчет количества тегов"""
        query = select(func.count()).select_from(Tags)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_with_trainings_count(self) -> List[tuple]:
        """Получение тегов с количеством тренингов"""
        query = (
            select(
                Tags,
                func.count(training_tags.c.training_uuid).label("trainings_count")
            )
            .outerjoin(training_tags, Tags.value == training_tags.c.tag_value)
            .group_by(Tags.value)
            .order_by(Tags.label)
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_trainings_by_tag(
            self,
            tag_value: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Training]:
        """Получение тренингов по тегу"""
        from sqlalchemy.orm import selectinload, joinedload
        from models.trainings import TrainingStep

        query = (
            select(Training)
            .join(training_tags, Training.uuid == training_tags.c.training_uuid)
            .where(training_tags.c.tag_value == tag_value)
            .options(
                selectinload(Training.tags),
                joinedload(Training.level),
                selectinload(Training.steps).selectinload(TrainingStep.action_type)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
