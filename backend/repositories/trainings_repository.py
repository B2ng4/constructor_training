from typing import List, Optional, Dict

from pydantic import UUID4
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from models.trainings import Training, TypesAction, TrainingStep, Tags, Levels, training_tags
from sqlalchemy import select, delete, update, func, exists


class TrainingRepository:
    """
    Репозиторий тренингов
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _get_eager_load_options(self):
        """
        Централизованные опции для eager loading всех relationships
        """
        return [
            selectinload(Training.tags),
            joinedload(Training.level),
            selectinload(Training.steps).selectinload(TrainingStep.action_type)
        ]

    async def create(self, training: Training) -> Training:
        """Создание тренинга"""
        self.session.add(training)
        await self.session.flush()
        await self.session.refresh(training)
        return training

    async def get_by_uuid(self, training_uuid: UUID4) -> Optional[Training]:
        """Получение тренинга по uuid БЕЗ relationships (базовый метод)"""
        query = select(Training).where(Training.uuid == training_uuid)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_uuid_with_relations(self, training_uuid: UUID4) -> Optional[Training]:
        """Получение тренинга по uuid СО ВСЕМИ relationships"""
        query = (
            select(Training)
            .options(*self._get_eager_load_options())
            .where(Training.uuid == training_uuid)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> List[Training]:
        """Получение всех тренингов пользователя БЕЗ relationships"""
        query = select(Training).where(Training.creator_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_user_id_with_relations(self, user_id: int) -> List[Training]:
        """Получение всех тренингов пользователя СО ВСЕМИ relationships"""
        query = (
            select(Training)
            .options(*self._get_eager_load_options())
            .where(Training.creator_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Training]:
        """Получение тренингов по фильтрам БЕЗ relationships"""
        query = select(Training).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_with_relations(self, skip: int = 0, limit: int = 100) -> List[Training]:
        """Получение тренингов по фильтрам СО ВСЕМИ relationships"""
        query = (
            select(Training)
            .options(*self._get_eager_load_options())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def patch_training_fields(self, training_uuid: UUID4, update_data: Dict) -> bool:
        """Частичное обновление полей тренинга"""
        if not update_data:
            return False

        query = (
            update(Training)
            .where(Training.uuid == training_uuid)
            .values(**update_data)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def create_training_step(self, step: TrainingStep) -> TrainingStep:
        """Создание шага тренинга"""
        self.session.add(step)
        await self.session.flush()
        await self.session.refresh(step)
        return step

    async def get_training_steps(self, training_uuid: UUID4) -> List[TrainingStep]:
        """Получение всех шагов тренинга по его uuid"""
        query = (
            select(TrainingStep)
            .options(selectinload(TrainingStep.action_type))
            .where(TrainingStep.training_uuid == training_uuid)
            .order_by(TrainingStep.step_number)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_training_step(self, step_id: int, update_data: Dict) -> bool:
        """Обновить шаг тренинга по id шага"""
        if not update_data:
            return False

        query = (
            update(TrainingStep)
            .where(TrainingStep.id == step_id)
            .values(**update_data)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def delete_training_step(self, step_id: int) -> bool:
        """Удалить шаг тренинга по id шага"""
        query = delete(TrainingStep).where(TrainingStep.id == step_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def delete(self, training_uuid: UUID4) -> bool:
        """Удаление тренинга"""
        query = delete(Training).where(Training.uuid == training_uuid)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def get_action_type(self, action_type_id: int) -> Optional[TypesAction]:
        """Получение типа шага тренинга по его id"""
        return await self.session.get(TypesAction, action_type_id)

    async def create_steps_from_photos(
            self,
            training_uuid: UUID4,
            photo_urls: List[str]
    ) -> List[Dict]:
        """Создание шагов тренинга из фотографий (скриншотов)"""
        existing_steps = await self.get_training_steps(training_uuid)
        next_step_number = len(existing_steps) + 1

        created_steps_info = []

        for i, photo_url in enumerate(photo_urls):
            step_number = next_step_number + i

            new_step = TrainingStep(
                step_number=step_number,
                training_uuid=training_uuid,
                image_url=photo_url
            )

            self.session.add(new_step)
            created_steps_info.append({
                "step_number": step_number,
                "image_url": photo_url
            })

        await self.session.flush()
        return created_steps_info

    async def check_training_exists(self, training_uuid: UUID4) -> bool:
        """Проверка существования тренинга по uuid"""
        query = select(exists().where(Training.uuid == training_uuid))
        result = await self.session.execute(query)
        return result.scalar_one()

    # === Методы для работы с тегами ===

    async def create_tag(self, name: str) -> Tags:
        """Создание нового тега"""
        tag = Tags(name=name)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def get_tag_by_id(self, tag_id: int) -> Optional[Tags]:
        """Получение тега по ID"""
        return await self.session.get(Tags, tag_id)

    async def get_tag_by_name(self, name: str) -> Optional[Tags]:
        """Получение тега по имени"""
        query = select(Tags).where(Tags.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_tags(self) -> List[Tags]:
        """Получение всех тегов"""
        query = select(Tags).order_by(Tags.name)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_tags_with_trainings_count(self) -> List[tuple]:
        """Получение всех тегов с количеством тренингов"""
        query = (
            select(
                Tags,
                func.count(training_tags.c.training_uuid).label("trainings_count")
            )
            .outerjoin(training_tags, Tags.id == training_tags.c.tag_id)
            .group_by(Tags.id)
            .order_by(Tags.name)
        )
        result = await self.session.execute(query)
        return result.all()

    async def update_tag(self, tag_id: int, name: str) -> Optional[Tags]:
        """Обновление тега"""
        query = (
            update(Tags)
            .where(Tags.id == tag_id)
            .values(name=name)
        )
        result = await self.session.execute(query)
        await self.session.commit()

        if result.rowcount > 0:
            return await self.get_tag_by_id(tag_id)
        return None

    async def delete_tag(self, tag_id: int) -> bool:
        """Удаление тега"""
        query = delete(Tags).where(Tags.id == tag_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def get_trainings_by_tag_id(
            self,
            tag_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Training]:
        """Получение всех тренингов с определенным тегом"""
        query = (
            select(Training)
            .join(training_tags, Training.uuid == training_tags.c.training_uuid)
            .where(training_tags.c.tag_id == tag_id)
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

    # === Методы для работы с уровнями ===

    async def get_level_by_id(self, level_id: int) -> Optional[Levels]:
        """Получение уровня по ID"""
        return await self.session.get(Levels, level_id)

    async def get_all_levels(self) -> List[Levels]:
        """Получение всех доступных уровней"""
        query = select(Levels).order_by(Levels.id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_level(self, name: str) -> Levels:
        """Создание нового уровня"""
        level = Levels(name=name)
        self.session.add(level)
        await self.session.commit()
        await self.session.refresh(level)
        return level

    async def update_level(self, level_id: int, name: str) -> Optional[Levels]:
        """Обновление уровня"""
        query = (
            update(Levels)
            .where(Levels.id == level_id)
            .values(name=name)
        )
        result = await self.session.execute(query)
        await self.session.commit()

        if result.rowcount > 0:
            return await self.get_level_by_id(level_id)
        return None

    async def delete_level(self, level_id: int) -> bool:
        """Удаление уровня"""
        query = delete(Levels).where(Levels.id == level_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
