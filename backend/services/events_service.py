
from repositories.events_repository import EventsRepository


class EventsService:
    def __init__(self, repo: EventsRepository):
        self.user_repo = repo