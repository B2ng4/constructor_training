from typing import List

from repositories.trainings_repository import TrainingRepository

from schemas.trainings import EventCreate, EventResponse, EventDetailResponse, EventUpdate




class TrainingsService:
    def __init__(self, repo: TrainingRepository):
        self.repo = repo

    async def create_event(self, event_data: EventCreate)->bool:
        return await self.repo.create(event_data)

    async def get_event(self, event_id: int) -> EventResponse:
        event = await self.repo.get_by_id(event_id)
        if not event:
            return None
        return EventResponse.model_validate(event)

    async def get_event_with_details(self, event_id: int) -> EventDetailResponse:
        event_data = await self.repo.get_with_type_details(event_id)
        if not event_data:
            return None
        event_response = EventResponse.model_validate(event_data["Event"])

        return EventDetailResponse(
            **event_response.model_dump(),
            type_name=event_data["type_name"],
            type_data=event_data["type_data"]
        )

    async def get_events(self, skip: int = 0, limit: int = 100) -> List[EventResponse]:
        events = await self.repo.get_all(skip, limit)
        return [EventResponse.model_validate(event) for event in events]

    async def update_event(self, event_id: int, event_data: EventUpdate) -> EventResponse:
        event = await self.repo.update(event_id, event_data)
        if not event:
            return None
        return EventResponse.model_validate(event)

    async def delete_event(self, event_id: int) -> bool:
        return await self.repo.delete(event_id)