
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from depends import get_trainings_service
from starlette import status
from services.trainings_service import TrainingsService

from schemas.trainings import TrainingResponse, TrainingUpdate, TrainingCreate

router = APIRouter(prefix="/trainings", tags=["Тренинги"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/create_training")

async def create_training(ser_data: TrainingCreate,
                       token: str = Depends(oauth2_scheme),
                       event_service: TrainingsService = Depends(get_trainings_service)):
    """Создание нового тренинга (только админы и суперпользователи"""
    if await event_service.create_training(ser_data):
        return HTTPException(status.HTTP_200_OK, detail="Тренинг успешно создан")
    else:
        return HTTPException(status_code=404, detail="Тренинг не создан")


@router.get("/{training_id}", response_model=TrainingResponse)
async def get_training(training_id: int,service: TrainingsService = Depends(get_trainings_service)):
    event = await service.get_training(training_id)
    if not event:
        raise HTTPException(status_code=404, detail="Тренинг не найден")
    return event


@router.put("/{training_id}")
async def update_event(
    event_id: int,
    event_data: TrainingUpdate,
    service: TrainingsService = Depends(get_trainings_service)):
    event = await service.update_training(event_id, event_data)
    if not event:
        raise HTTPException(status_code=404, detail="Тренинг не найден")

    return HTTPException(status_code=200, detail="Данные тренинга успешно обновлены")


@router.delete("/{training_id}")
async def delete_event(training_id: int, service: TrainingsService = Depends(get_trainings_service)):
    if await service.delete_training(training_id):
        return HTTPException(status.HTTP_200_OK, detail="Тренинг успешно удален")
    else:
        raise HTTPException(status_code=404, detail="Тренинг не найден")

#TODO: Добавить доступ к апихам по ролям, добавить ручки для получения тренингов по типу(фильтрация)

