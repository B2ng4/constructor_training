
from repositories.events_repository import EventsRepository

from schemas.events import EventCreate


class EventsService:
    def __init__(self, repo: EventsRepository):
        self.events_repo = repo

    async def create_event(self, event_data: EventCreate)->bool:
        return await self.events_repo.create(event_data)

