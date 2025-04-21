from typing import Optional

from pydantic import UUID4
from sqlalchemy.orm import selectinload

from schemas.trainings import TrainingCreate, TrainingUpdate
from models.trainings import Training, Image, TypesAction, TrainingStep
from sqlalchemy import select, delete, update


class TrainingRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def create(self, training: Training) -> Training:
        self.session.add(training)
        await self.session.commit()
        await self.session.refresh(training, attribute_names=["steps", "cover_image"])
        return training


    async def get_by_id(self, training_id: int) -> Optional[Training]:
        query = (
            select(Training)
            .options(
                selectinload(Training.steps)
                .selectinload(TrainingStep.action_type),
                selectinload(Training.steps)
                .selectinload(TrainingStep.image)
            )
            .where(Training.id == training_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_by_user_id(self, user_id: int) -> Optional[Training]:
        query = (
            select(Training)
            .options(
                selectinload(Training.steps)
                .selectinload(TrainingStep.action_type),
                selectinload(Training.steps)
                .selectinload(TrainingStep.image)
            )
            .where(Training.creator_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()




    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Training]:
        query = select(Training).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, event_id: int, training_data: TrainingUpdate) -> Training:
        update_data = training_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(event_id)

        query = (
            update(Training)
            .where(Training.id == event_id)
            .values(**update_data)
            .returning(Training)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()

    async def delete(self, event_id: int) -> bool:
        query = delete(Training).where(Training.id == event_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0


    async def get_image(self, image_uuid: UUID4) -> Image:
        return await self.session.get(Image, image_uuid)


    async def get_action_type(self, action_type_id: int) -> TypesAction:
        return await self.session.get(TypesAction, action_type_id)

