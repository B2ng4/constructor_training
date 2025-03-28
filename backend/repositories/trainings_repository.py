from schemas.trainings import EventCreate, EventUpdate
from models.events import Event
from sqlalchemy import select, delete, update

from models.events import Name_event, Type_event


class TrainingRepository:
    def __init__(self, session) -> None:
        self.session = session
    async def create(self, event_data: EventCreate) -> bool:
        new_event = Event(**event_data.model_dump(exclude_unset=True))
        self.session.add(new_event)
        await self.session.commit()
        return True

    async def get_by_id(self, event_id: int) -> Event:
        query = select(Event).where(Event.id == event_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Event]:
        query = select(Event).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, event_id: int, event_data: EventUpdate) -> Event:
        update_data = event_data.dict(exclude_unset=True)
        if not update_data:
            # Если нет данных для обновления, просто возвращаем существующее событие
            return await self.get_by_id(event_id)

        query = update(Event).where(Event.id == event_id).values(**update_data).returning(Event)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()

    async def delete(self, event_id: int) -> bool:
        query = delete(Event).where(Event.id == event_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def get_with_type_details(self, event_id: int):
        query = (
            select(
                Event,
                Name_event.name.label("type_name"),
                Type_event.data.label("type_data")
            )
            .join(Type_event, Event.type_id == Type_event.id)
            .join(Name_event, Type_event.name == Name_event.id)
            .where(Event.id == event_id)
        )
        result = await self.session.execute(query)
        return result.mappings().one_or_none()