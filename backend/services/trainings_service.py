from typing import List, Optional, Dict, Union, Any
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.trainings_repository import TrainingRepository
from backend.schemas.trainings import (
    TrainingCreate,
    TrainingResponse,
    TrainingUpdate,
    TrainingStepCreate,
    TrainingStepUpdate,
    TrainingStepResponse, TrainingListResponse
)

from backend.models.trainings import Training, TrainingStep, TypesAction, Tags
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


class TrainingsService:
    def __init__(self, session: AsyncSession):
        self.repo = TrainingRepository(session)
        self.session = session

    async def create_training(
            self,
            training_data: TrainingCreate,
            creator_id: int
    ):
        """Создание тренинга с тегами и шагами"""
        try:
            training_dict = training_data.model_dump(
                exclude={"steps", "tag_ids"}
            )

            training = Training(**training_dict, creator_id=creator_id)

            if training_data.tag_ids:
                tags_result = await self.session.execute(
                    select(Tags).where(Tags.value.in_(training_data.tag_ids))
                )
                tags = tags_result.scalars().all()
                training.tags = list(tags)

            created_training = await self.repo.create(training)
            if not created_training:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create training"
                )

            if training_data.steps:
                for step_data in training_data.steps:
                    step = await self.create_training_step(step_data)
                    step.training_uuid = created_training.uuid
                    await self.repo.create_training_step(step)

            await self.session.commit()

            created_training = await self.repo.get_by_uuid_with_relations(created_training.uuid)

            if created_training:
                return TrainingResponse.model_validate(created_training)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created training"
            )

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating training: {str(e)}"
            )

    async def create_training_step(
            self,
            step_data: TrainingStepCreate
    ) -> TrainingStep:
        """Создание шага тренинга"""
        if step_data.action_type_id:
            action_type = await self.repo.get_action_type(step_data.action_type_id)
            if not action_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Action type with ID {step_data.action_type_id} not found"
                )

            step_dict = step_data.model_dump(exclude={"action_type_id"})
            return TrainingStep(**step_dict, action_type=action_type)
        else:
            step_dict = step_data.model_dump(exclude={"action_type_id"})
            return TrainingStep(**step_dict)

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
            self,
            skip: int = 0,
            limit: int = 100
    ) -> List[TrainingResponse]:
        """Получение списка тренингов с пагинацией"""
        trainings = await self.repo.get_all_with_relations(skip, limit)
        return [TrainingResponse.model_validate(t) for t in trainings]

    async def get_trainings_by_user_id(
            self,
            user_id: int
    ) -> List[TrainingListResponse]:  # ✅ ИЗМЕНЕНО
        """Получение тренингов пользователя БЕЗ шагов"""
        trainings = await self.repo.get_by_user_id(user_id)  # ✅ БЕЗ _with_relations
        return [TrainingListResponse.model_validate(training) for training in trainings]  # ✅ TrainingListResponse


    async def patch_training(
            self,
            training_uuid: UUID4,
            training_data: TrainingUpdate
    ) -> TrainingResponse:
        """Частичное обновление тренинга и его шагов"""
        try:
            existing_training = await self.repo.get_by_uuid_with_relations(training_uuid)
            if not existing_training:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Training not found"
                )

            update_data = training_data.model_dump(
                exclude_unset=True,
                exclude={"steps", "tag_ids"}
            )
            if update_data:
                await self.repo.patch_training_fields(training_uuid, update_data)

            if hasattr(training_data, 'tag_ids') and training_data.tag_ids is not None:
                tags_result = await self.session.execute(
                    select(Tags).where(Tags.value.in_(training_data.tag_ids))
                )
                tags = tags_result.scalars().all()
                existing_training.tags = list(tags)
                await self.session.flush()

            if hasattr(training_data, 'steps') and training_data.steps is not None:
                await self.patch_training_steps(training_uuid, training_data.steps)

            await self.session.commit()

            updated_training = await self.repo.get_by_uuid_with_relations(training_uuid)
            return TrainingResponse.model_validate(updated_training)

        except HTTPException:
            await self.session.rollback()
            raise
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
                update_data = step_data.model_dump(exclude_unset=True, exclude={"id"})
                if update_data:
                    await self.repo.update_training_step(step_id, update_data)
            elif not step_id:
                step = await self.create_training_step(step_data)
                step.training_uuid = training_uuid
                await self.repo.create_training_step(step)

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
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Training with UUID {training_uuid} not found"
                )

            result = await self.repo.create_steps_from_photos(training_uuid, photo_urls)

            await self.session.commit()

            return result
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating steps from photos: {str(e)}"
            )

    async def add_step(
            self,
            training_uuid: UUID4,
            step_data: TrainingStepCreate
    ) -> TrainingStepResponse:
        """Добавление одного шага к тренингу"""
        try:
            # Проверяем существование тренинга
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Training with UUID {training_uuid} not found"
                )

            # Создаем шаг
            step = await self.create_training_step(step_data)
            step.training_uuid = training_uuid
            created_step = await self.repo.create_training_step(step)

            await self.session.commit()
            await self.session.refresh(created_step)

            return TrainingStepResponse.model_validate(created_step)

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error adding step: {str(e)}"
            )

    async def add_steps_bulk(
            self,
            training_uuid: UUID4,
            steps_data: List[TrainingStepCreate]
    ) -> List[TrainingStepResponse]:
        """Массовое добавление шагов к тренингу"""
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Training with UUID {training_uuid} not found"
                )

            created_steps = []
            for step_data in steps_data:
                step = await self.create_training_step(step_data)
                step.training_uuid = training_uuid
                created_step = await self.repo.create_training_step(step)
                created_steps.append(created_step)

            await self.session.commit()

            # Обновляем объекты после коммита
            for step in created_steps:
                await self.session.refresh(step)

            return [TrainingStepResponse.model_validate(step) for step in created_steps]

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error adding steps: {str(e)}"
            )

    async def update_step(
            self,
            step_id: int,
            step_data: TrainingStepUpdate
    ) -> TrainingStepResponse:
        """Обновление одного шага"""
        try:
            # Проверяем существование шага
            existing_step = await self.repo.get_step_by_id(step_id)
            if not existing_step:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Step with ID {step_id} not found"
                )

            update_data = step_data.model_dump(exclude_unset=True, exclude={"id", "steps"})

            if update_data:
                await self.repo.update_training_step(step_id, update_data)

            await self.session.commit()

            # Получаем обновленный шаг
            updated_step = await self.repo.get_step_by_id(step_id)
            return TrainingStepResponse.model_validate(updated_step)

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating step: {str(e)}"
            )

    async def delete_step(
            self,
            step_id: int
    ) -> bool:
        """Удаление одного шага"""
        try:
            success = await self.repo.delete_training_step(step_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Step with ID {step_id} not found"
                )

            await self.session.commit()
            return True

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting step: {str(e)}"
            )

    async def delete_steps_bulk(
            self,
            step_ids: List[int]
    ) -> Dict[str, Any]:
        """Массовое удаление шагов"""
        try:
            deleted_count = 0
            not_found = []

            for step_id in step_ids:
                success = await self.repo.delete_training_step(step_id)
                if success:
                    deleted_count += 1
                else:
                    not_found.append(step_id)

            await self.session.commit()

            return {
                "deleted": deleted_count,
                "not_found": not_found,
                "total_requested": len(step_ids)
            }

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting steps: {str(e)}"
            )