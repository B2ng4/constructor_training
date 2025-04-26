from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.trainings_repository import TrainingRepository
from schemas.trainings import (
    TrainingCreate,
    TrainingResponse,
    TrainingUpdate,
    TrainingStepCreate,
)
from models.trainings import Training, TrainingStep, Image, TypesAction
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


class TrainingsService:
    def __init__(self, session: AsyncSession):
        self.repo = TrainingRepository(session)
        self.session = session

    async def create_training(
            self, training_data: TrainingCreate, creator_id: int
    ):
        training_dict = training_data.model_dump(
            exclude={"steps", "cover_image"}
            )
        training = Training(**training_dict, creator_id=creator_id)

        if training_data.cover_image:
            cover_image = await self._get_image(training_data.cover_image)
            training.cover_image = cover_image.uuid
        for step_data in training_data.steps:
            step = await self._create_training_step(step_data)
            step.training_id = training.id
            training.steps.append(step)
        created_training = await self.repo.create(training)
        if created_training:
            return TrainingResponse.model_validate(created_training)
        return False



    async def _create_training_step(
        self, step_data: TrainingStepCreate
    ) -> TrainingStep:
        action_type = await self._get_action_type(step_data.action_type_id)
        image = await self._get_image(step_data.image_uuid)
        step_dict = step_data.model_dump(exclude={"image_uuid", "action_type_id"})
        return TrainingStep(
            **step_dict,
            action_type=action_type,
            image=image
        )

    async def _get_image(self, image_uuid: str) -> Image:
        image = await self.repo.get_image(image_uuid)
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with UUID {image_uuid} not found"
            )
        return image

    async def _get_action_type(self, action_type_id: int) -> TypesAction:
        action_type = await self.repo.get_action_type(action_type_id)
        if not action_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action type with ID {action_type_id} not found"
            )
        return action_type

    async def get_training(self, training_uuid: UUID4) -> TrainingResponse:
        training = await self.repo.get_by_uuid(training_uuid)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training not found"
            )
        return TrainingResponse.model_validate(training)


    async def get_trainings_by_params(
            self, skip: int = 0, limit: int = 100
    ) -> List[TrainingResponse]:
        trainings = await self.repo.get_all(skip, limit)
        return [TrainingResponse.model_validate(t) for t in trainings]




    async def get_trainings_by_user_id(
            self, user_id:int
    ) -> List[TrainingResponse]:
        trainings = await self.repo.get_by_user_id(user_id)
        return [TrainingResponse.model_validate(training) for training in trainings]





    async def update_training(
            self, training_id: int, training_data: TrainingUpdate
    ) -> TrainingResponse:
        try:
            training = await self.repo.update(training_id, training_data)
            if not training:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Training not found"
                )
            return TrainingResponse.model_validate(training)
        except IntegrityError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Update error: {str(e)}"
            )

    async def delete_training(self, training_uuid: UUID4) -> bool:
        success = await self.repo.delete(training_uuid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training not found"
            )
        return True