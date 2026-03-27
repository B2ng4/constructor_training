from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.courses import Course
from repositories.courses_repository import CoursesRepository
from schemas.courses import CourseCreate, CourseListResponse


class CoursesService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CoursesRepository(session)

    async def create_course(
        self, course_data: CourseCreate, creator_id: int
    ) -> CourseListResponse:
        try:
            normalized_title = course_data.title.strip()
            if not normalized_title:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Название курса не может быть пустым",
                )

            unique_training_uuids = list(dict.fromkeys(course_data.training_uuids))

            course = Course(
                title=normalized_title,
                description=course_data.description,
                creator_id=creator_id,
            )

            trainings = await self.repo.get_training_by_uuids(unique_training_uuids)
            if len(trainings) != len(unique_training_uuids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Некоторые тренинги не найдены",
                )

            if any(training.creator_id != creator_id for training in trainings):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Можно добавлять в курс только свои тренинги",
                )

            course.trainings = trainings
            created_course = await self.repo.create(course)
            await self.session.commit()

            courses = await self.repo.get_by_user_id(creator_id)
            response_course = next(
                (item for item in courses if item.id == created_course.id), None
            )
            if not response_course:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Не удалось получить созданный курс",
                )
            return CourseListResponse.model_validate(response_course)
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка создания курса: {str(e)}",
            )

    async def get_courses_by_user_id(self, user_id: int) -> List[CourseListResponse]:
        courses = await self.repo.get_by_user_id(user_id)
        return [CourseListResponse.model_validate(course) for course in courses]

    async def delete_course(self, course_id: int, user_id: int) -> bool:
        course = await self.repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден"
            )
        if course.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к курсу"
            )
        deleted = await self.repo.delete(course_id)
        await self.session.commit()
        return deleted
