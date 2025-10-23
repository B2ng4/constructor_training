from typing import List, Optional, Dict, Union

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.trainings_repository import TrainingRepository
from schemas.trainings import (
    TrainingCreate,
    TrainingResponse,
    TrainingUpdate,
    TrainingStepCreate,
    TrainingStepUpdate,
)
from models.trainings import Training, TrainingStep, TypesAction, Tags
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


class TrainingsService:
    def __init__(self, session: AsyncSession):
        self.repo = TrainingRepository(session)
        self.session = session

    async def create_training(
            self, training_data: TrainingCreate, creator_id: int
    ):
        """Создание тренинга с тегами и шагами"""
        training_dict = training_data.model_dump(
            exclude={"steps", "tag_ids"}
        )
        training = Training(**training_dict, creator_id=creator_id)

        # Добавляем теги, если они указаны
        if training_data.tag_ids:
            tags_result = await self.session.execute(
                select(Tags).where(Tags.id.in_(training_data.tag_ids))
            )
            tags = tags_result.scalars().all()
            training.tags = list(tags)

        created_training = await self.repo.create(training)
        if not created_training:
            return False

        # Создаем шаги
        for step_data in training_data.steps:
            step = await self.create_training_step(step_data)
            step.training_uuid = created_training.uuid
            await self.repo.create_training_step(step)

        # Загружаем тренинг со всеми relationships
        created_training = await self.repo.get_by_uuid_with_relations(created_training.uuid)

        if created_training:
            return TrainingResponse.model_validate(created_training)
        return False

    async def create_training_step(
            self, step_data: TrainingStepCreate
    ) -> TrainingStep:
        """Создание шага тренинга"""
        action_type = await self.repo.get_action_type(step_data.action_type_id)
        if not action_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action type with ID {step_data.action_type_id} not found"
            )

        step_dict = step_data.model_dump(exclude={"action_type_id"})
        return TrainingStep(**step_dict, action_type=action_type)

    async def get_training(self, training_uuid: UUID4) -> TrainingResponse:
        """Получение тренинга по UUID с загрузкой всех relationships"""
        training = await self.repo.get_by_uuid_with_relations(training_uuid)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training not found"
            )
        return TrainingResponse.model_validate(training)

    async def get_trainings_by_params(
            self, skip: int = 0, limit: int = 100
    ) -> List[TrainingResponse]:
        """Получение списка тренингов с пагинацией"""
        trainings = await self.repo.get_all_with_relations(skip, limit)
        return [TrainingResponse.model_validate(t) for t in trainings]

    async def get_trainings_by_user_id(
            self, user_id: int
    ) -> List[TrainingResponse]:
        """Получение тренингов пользователя с загрузкой relationships"""
        trainings = await self.repo.get_by_user_id_with_relations(user_id)
        return [TrainingResponse.model_validate(training) for training in trainings]

    async def patch_training(
            self, training_uuid: UUID4, training_data: TrainingUpdate
    ) -> TrainingResponse:
        """Частичное обновление тренинга и его шагов"""
        try:
            existing_training = await self.repo.get_by_uuid_with_relations(training_uuid)
            if not existing_training:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Training not found"
                )

            # Обновляем основные поля
            update_data = training_data.model_dump(
                exclude_unset=True,
                exclude={"steps", "tag_ids"}
            )
            if update_data:
                await self.repo.patch_training_fields(training_uuid, update_data)

            # Обновляем теги, если указаны
            if hasattr(training_data, 'tag_ids') and training_data.tag_ids is not None:
                tags_result = await self.session.execute(
                    select(Tags).where(Tags.id.in_(training_data.tag_ids))
                )
                tags = tags_result.scalars().all()
                existing_training.tags = list(tags)
                await self.session.flush()

            # Обновляем шаги
            if hasattr(training_data, 'steps') and training_data.steps is not None:
                await self.patch_training_steps(training_uuid, training_data.steps)

            await self.session.commit()

            # Загружаем обновленный тренинг со всеми relationships
            updated_training = await self.repo.get_by_uuid_with_relations(training_uuid)
            return TrainingResponse.model_validate(updated_training)

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )

    async def patch_training_steps(
            self,
            training_uuid: UUID4,
            steps_data: List[Union[TrainingStepCreate, TrainingStepUpdate]]
    ):
        """Частичное обновление шагов тренинга"""
        existing_steps = await self.repo.get_training_steps(training_uuid)
        existing_steps_dict = {step.id: step for step in existing_steps}

        for step_data in steps_data:
            step_id = getattr(step_data, 'id', None)

            if step_id and step_id in existing_steps_dict:
                # Обновляем существующий шаг
                update_data = step_data.model_dump(exclude_unset=True, exclude={"id"})
                if update_data:
                    await self.repo.update_training_step(step_id, update_data)
            elif not step_id:
                # Создаем новый шаг
                step_dict = step_data.model_dump(exclude_unset=True)
                step_dict['training_uuid'] = training_uuid
                new_step = TrainingStep(**step_dict)
                await self.repo.create_training_step(new_step)

    async def delete_training(self, training_uuid: UUID4) -> bool:
        """Удаление тренинга"""
        success = await self.repo.delete(training_uuid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training not found"
            )
        return True

    async def get_training_steps(self, training_uuid: UUID4) -> List[TrainingStep]:
        """Получение шагов тренинга"""
        return await self.repo.get_training_steps(training_uuid)

    async def create_steps_from_photos(
            self,
            training_uuid: UUID4,
            photo_urls: List[str]
    ) -> List[Dict]:
        """Создание шагов из фотографий"""
        training_exists = await self.repo.check_training_exists(training_uuid)
        if not training_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training with UUID {training_uuid} not found"
            )
        return await self.repo.create_steps_from_photos(training_uuid, photo_urls)
