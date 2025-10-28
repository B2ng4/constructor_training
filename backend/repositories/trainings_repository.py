from typing import List, Optional, Dict

from pydantic import UUID4
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.trainings import Training, TypesAction, TrainingStep
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


    async def get_step_by_id(self, step_id: int) -> Optional[TrainingStep]:
        """Получение шага по ID"""
        query = (
            select(TrainingStep)
            .options(selectinload(TrainingStep.action_type))
            .where(TrainingStep.id == step_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()