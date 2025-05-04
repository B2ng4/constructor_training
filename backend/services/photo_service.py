from typing import List

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from models.trainings import Training
from repositories.photo_repository import PhotoRepository


class PhotoService:
    def __init__(self, session: AsyncSession):
        self.repo = PhotoRepository(session)
        self.session = session

    async def get_all_photos(self, training_uuid: UUID4) -> List[str]:
        photo_urls = await self.repo.get_photos_by_training(training_uuid)
        return photo_urls
