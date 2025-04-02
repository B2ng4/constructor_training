from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.trainings_repository import TrainingRepository
from schemas.trainings import (
    TrainingCreate,
    TrainingResponse,
    TrainingDetailResponse,
    TrainingUpdate,
    TrainingStepCreate
)
from models.trainings import Training, TrainingStep, Image, TypesAction
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


class TrainingsService:
    def __init__(self, session: AsyncSession):
        self.repo = TrainingRepository(session)
        self.session = session
    async def create_training(self, training_data: TrainingCreate, creator_id: int) -> TrainingResponse:
        try:
            training_dict = training_data.model_dump(exclude={"steps", "cover_image_uuid"})
            training = Training(**training_dict, creator_id=creator_id)

            if training_data.cover_image_uuid:
                cover_image = await self._get_image(training_data.cover_image_uuid)
                training.cover_image = cover_image

            # Создаем шаги тренинга
            training.steps = []
            for step_data in training_data.steps:
                step = await self._create_training_step(step_data)
                training.steps.append(step)

            # Сохраняем в БД
            created_training = await self.repo.create(training)
            await self.session.commit()

            return TrainingResponse.model_validate(created_training)

        except IntegrityError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка целостности данных: " + str(e)
            )

    async def _create_training_step(self, step_data: TrainingStepCreate) -> TrainingStep:
        # Валидация типа действия
        action_type = await self.session.get(TypesAction, step_data.action_type_id)
        if not action_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Тип действия с ID {step_data.action_type_id} не найден"
            )

        image = await self._get_image(step_data.image_uuid)

        # Создаем шаг
        step_dict = step_data.model_dump(exclude={"image_uuid", "action_type_id"})
        return TrainingStep(
            **step_dict,
            action_type=action_type,
            image=image
        )

    async def _get_image(self, image_uuid: str) -> Image:
        image = await self.session.get(Image, image_uuid)
        if not image:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Изображение с UUID {image_uuid} не найдено"
            )
        return image

    async def get_training(self, Training_id: int) -> TrainingResponse:
        Training = await self.repo.get_by_id(Training_id)
        if not Training:
            return None
        return TrainingResponse.model_validate(Training)

    async def get_training_with_details(
        self, Training_id: int
    ) -> TrainingDetailResponse:
        Training_data = await self.repo.get_with_type_details(Training_id)
        if not Training_data:
            return None
        Training_response = TrainingResponse.model_validate(Training_data["Training"])

        return TrainingDetailResponse(
            **Training_response.model_dump(),
            type_name=Training_data["type_name"],
            type_data=Training_data["type_data"]
        )

    async def get_trainings(
        self, skip: int = 0, limit: int = 100
    ) -> List[TrainingResponse]:
        Trainings = await self.repo.get_all(skip, limit)
        return [TrainingResponse.model_validate(Training) for Training in Trainings]

    async def update_training(
        self, Training_id: int, Training_data: TrainingUpdate
    ) -> TrainingResponse:
        Training = await self.repo.update(Training_id, Training_data)
        if not Training:
            return None
        return TrainingResponse.model_validate(Training)

    async def delete_training(self, Training_id: int) -> bool:
        return await self.repo.delete(Training_id)
