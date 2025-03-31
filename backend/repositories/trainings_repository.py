from schemas.trainings import TrainingCreate, TrainingUpdate
from models.trainings import Training
from sqlalchemy import select, delete, update


class TrainingRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def create(self, event_data: TrainingCreate) -> bool:
        new_event = Training(**event_data.model_dump(exclude_unset=True))
        self.session.add(new_event)
        await self.session.commit()
        return True

    async def get_by_id(self, Training_id: int) -> Training:
        query = select(Training).where(Training.id == Training_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Training]:
        query = select(Training).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, event_id: int, training_data: TrainingUpdate) -> Training:
        update_data = training_data.dict(exclude_unset=True)
        if not update_data:
            # Если нет данных для обновления, просто возвращаем существующее событие
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
