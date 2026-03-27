from fastapi import APIRouter, Depends, HTTPException, status

from depends import get_courses_service, get_user_service, oauth2_scheme
from schemas.courses import CourseCreate, CourseListResponse
from services.courses_service import CoursesService
from services.user_service import UserService

router = APIRouter(prefix="/course", tags=["Курсы"])


@router.post("/create_course", response_model=CourseListResponse, name="Создание курса")
async def create_course(
    ser_data: CourseCreate,
    token: str = Depends(oauth2_scheme),
    course_service: CoursesService = Depends(get_courses_service),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_current_user(token)
    created_course = await course_service.create_course(ser_data, user.id)
    if not created_course:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Курс не создан",
        )
    return created_course


@router.get(
    "/my_courses",
    response_model=list[CourseListResponse],
    name="Получение курсов пользователя",
)
async def get_my_courses(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
    course_service: CoursesService = Depends(get_courses_service),
):
    user = await user_service.get_current_user(token)
    return await course_service.get_courses_by_user_id(user.id)


@router.delete("/{course_id}", name="Удаление курса")
async def delete_course(
    course_id: int,
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
    course_service: CoursesService = Depends(get_courses_service),
):
    user = await user_service.get_current_user(token)
    await course_service.delete_course(course_id, user.id)
    return {"detail": "Курс успешно удален"}
