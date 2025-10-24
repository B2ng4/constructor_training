# routing/tags_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError

from schemas.tags import TagCreate, TagUpdate, TagResponse, TagWithTrainingsCount
from schemas.trainings import TrainingListResponse
from repositories.tags_repository import TagsRepository
from backend.depends import get_tags_repository, get_current_user
from models.users import User

router = APIRouter(prefix="/tags", tags=["Теги"])


@router.post(
    "/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание тега"
)
async def create_tag(
        tag_data: TagCreate,
        repo: TagsRepository = Depends(get_tags_repository),
        current_user: User = Depends(get_current_user)
):
    """Создать новый тег"""
    # Проверка уникальности
    existing = await repo.get_by_name(tag_data.label)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Тег '{tag_data.label}' уже существует"
        )

    try:
        tag = await repo.create(label=tag_data.label)
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
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        repo: TagsRepository = Depends(get_tags_repository)
):
    """Получить список всех тегов"""
    tags = await repo.get_all(skip=skip, limit=limit, order_by="label")
    return [TagResponse.model_validate(tag) for tag in tags]


@router.get(
    "/with-count",
    response_model=List[TagWithTrainingsCount],
    summary="Получение тегов с количеством тренингов"
)
async def get_tags_with_count(
        repo: TagsRepository = Depends(get_tags_repository)
):
    """Получить теги с количеством тренингов"""
    tags_with_count = await repo.get_with_trainings_count()

    return [
        TagWithTrainingsCount(
            value=tag.value,
            label=tag.label,
            trainings_count=count
        )
        for tag, count in tags_with_count
    ]


@router.get(
    "/{tag_value}",
    response_model=TagResponse,
    summary="Получение тега по ID"
)
async def get_tag_by_id(
        tag_value: int,
        repo: TagsRepository = Depends(get_tags_repository)
):
    """Получить тег по value (ID)"""
    tag = await repo.get_by_id(tag_value)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_value} не найден"
        )
    return TagResponse.model_validate(tag)


@router.get(
    "/{tag_value}/trainings",
    response_model=List[TrainingListResponse],
    summary="Получение тренингов по тегу"
)
async def get_trainings_by_tag(
        tag_value: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        repo: TagsRepository = Depends(get_tags_repository)
):
    """Получить тренинги по тегу"""
    if not await repo.exists(tag_value):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_value} не найден"
        )

    trainings = await repo.get_trainings_by_tag(tag_value, skip, limit)
    return [TrainingListResponse.model_validate(t) for t in trainings]


@router.patch(
    "/{tag_value}",
    response_model=TagResponse,
    summary="Обновление тега"
)
async def update_tag(
        tag_value: int,
        tag_data: TagUpdate,
        repo: TagsRepository = Depends(get_tags_repository),
        current_user: User = Depends(get_current_user)
):
    """Обновить тег"""
    if not tag_data.label:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать новое название"
        )

    if not await repo.exists(tag_value):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_value} не найден"
        )

    # Проверка уникальности
    existing = await repo.get_by_name(tag_data.label)
    if existing and existing.value != tag_value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Тег '{tag_data.label}' уже существует"
        )

    try:
        updated = await repo.update(tag_value, tag_data.label)
        return TagResponse.model_validate(updated)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ошибка при обновлении тега"
        )


@router.delete(
    "/{tag_value}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление тега"
)
async def delete_tag(
        tag_value: int,
        repo: TagsRepository = Depends(get_tags_repository),
        current_user: User = Depends(get_current_user)
):
    """Удалить тег"""
    if not await repo.exists(tag_value):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_value} не найден"
        )

    success = await repo.delete(tag_value)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении тега"
        )
