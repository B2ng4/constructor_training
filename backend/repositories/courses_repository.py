from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.courses import Course
from models.trainings import Training


class CoursesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, course: Course) -> Course:
        self.session.add(course)
        await self.session.flush()
        await self.session.refresh(course)
        return course

    async def get_training_by_uuids(self, training_uuids: List[UUID]) -> List[Training]:
        if not training_uuids:
            return []
        query = (
            select(Training)
            .options(selectinload(Training.level))
            .where(Training.uuid.in_(training_uuids))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int) -> List[Course]:
        query = (
            select(Course)
            .options(selectinload(Course.trainings).selectinload(Training.level))
            .where(Course.creator_id == user_id)
            .order_by(Course.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().unique().all())

    async def get_by_id(self, course_id: int) -> Optional[Course]:
        query = select(Course).where(Course.id == course_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, course_id: int) -> bool:
        query = delete(Course).where(Course.id == course_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0
