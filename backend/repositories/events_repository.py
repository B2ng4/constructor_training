from schemas.events import EventCreate
from models.events import Event


class EventsRepository:
    def __init__(self, session) -> None:
        self.session = session
    async def create(self, event_data: EventCreate) -> bool:
        new_event = Event(
            title=event_data.title,
            type_id=event_data.type_id,
            start_date=event_data.start_date,
            end_date=event_data.end_date
        )
        self.session.add(new_event)
        await self.session.commit()
        return True

