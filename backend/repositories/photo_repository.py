import uuid
from typing import List

from sqlalchemy import select, delete, update, UUID

from models.trainings import Image


class PhotoRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def add_photo(self, training_uuid: UUID, url: str) -> None:
        new_image = Image(
            uuid=uuid.uuid4(),
            url=url,
            training_uuid=training_uuid
        )
        self.session.add(new_image)
        await self.session.commit()

    async def get_photos_by_training(self, training_uuid: UUID) -> List[str]:
        query = select(Image.url).where(Image.training_uuid == training_uuid)
        result = await self.session.execute(query)
        return result.scalars().all()
