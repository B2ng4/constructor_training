# routing/tags_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError

from schemas.tags import TagCreate, TagUpdate, TagResponse, TagWithTrainingsCount
from schemas.trainings import TrainingListResponse
from repositories.trainings_repository import TrainingRepository
from backend.depends import get_trainings_repository, get_current_user
from models.users import User

router = APIRouter(prefix="/tags", tags=["Теги"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post(
    "/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание тега"
)
async def create_tag(
        tag_data: TagCreate,
        repo: TrainingRepository = Depends(get_trainings_repository),
        token: str = Depends(oauth2_scheme),
):
    """
    Создать новый тег.

    - **name**: название тега (уникальное, 1-50 символов)
    """
    # Проверка на существование
    existing_tag = await repo.get_tag_by_name(tag_data.name)
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Тег с именем '{tag_data.name}' уже существует"
        )

    try:
        tag = await repo.create_tag(tag_data.name)
        return TagResponse.model_validate(tag)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ошибка при создании тега"
        )


@router.get(
    "/",
    response_model=List[TagResponse],
    summary="Получение всех тегов"
)
async def get_all_tags(
        repo: TrainingRepository = Depends(get_trainings_repository)
):
    """
    Получить список всех тегов
    """
    tags = await repo.get_all_tags()
    return [TagResponse.model_validate(tag) for tag in tags]


@router.get(
    "/with-count",
    response_model=List[TagWithTrainingsCount],
    summary="Получение тегов с количеством тренингов"
)



@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Получение тега по ID"
)
async def get_tag_by_id(
        tag_id: int,
        repo: TrainingRepository = Depends(get_trainings_repository)
):
    """
    Получить тег по его ID.

    - **tag_id**: идентификатор тега
    """
    tag = await repo.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_id} не найден"
        )
    return TagResponse.model_validate(tag)


@router.get(
    "/{tag_id}/trainings",
    response_model=List[TrainingListResponse],
    summary="Получение тренингов по тегу"
)
async def get_trainings_by_tag(
        tag_id: int,
        skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
        limit: int = Query(100, ge=1, le=500, description="Максимальное количество записей"),
        repo: TrainingRepository = Depends(get_trainings_repository)
):
    """
    Получить все тренинги с указанным тегом.

    - **tag_id**: идентификатор тега
    - **skip**: пропустить N записей
    - **limit**: максимум записей на страницу
    """
    # Проверяем существование тега
    tag = await repo.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_id} не найден"
        )

    trainings = await repo.get_trainings_by_tag_id(tag_id, skip, limit)
    return [TrainingListResponse.model_validate(t) for t in trainings]


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление тега"
)
async def delete_tag(
        tag_id: int,
        repo: TrainingRepository = Depends(get_trainings_repository),
        token: str = Depends(oauth2_scheme),
):
    """
    Удалить тег.

    - **tag_id**: идентификатор тега
    """
    # Проверяем существование тега
    tag = await repo.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_id} не найден"
        )

    success = await repo.delete_tag(tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении тега"
        )

    return None


