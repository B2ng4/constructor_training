from typing import List

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4
from fastapi.responses import JSONResponse
from depends import get_trainings_service, get_s3_service, get_user_service
from starlette import status
from services.trainings_service import TrainingsService
from services.external_services.s3_service import S3Service
from schemas.trainings import TrainingResponse, TrainingUpdate, TrainingCreate, TrainingListResponse
from services.user_service import UserService

from schemas.trainings import TrainingStepResponse, TrainingStepCreate, StepBulkCreateRequest, \
    TrainingStepUpdate


router = APIRouter(prefix="/training", tags=["Тренинги"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/create_training", name="Создание тренинга")
async def create_training(
    ser_data: TrainingCreate,
    token: str = Depends(oauth2_scheme),
    training_service: TrainingsService = Depends(get_trainings_service),
    user_service: UserService = Depends(get_user_service),
):
    """Создание нового тренинга"""
    creator_id = await user_service.get_current_user(token)
    created_training = await training_service.create_training(ser_data, creator_id.id)

    if created_training:
        return {"status": status.HTTP_201_CREATED,
                "data": created_training.dict()}
    else:
        raise HTTPException(status_code=404, detail="Тренинг не создан")




@router.get("/{training_uuid}", name="Получение конкретного тренинга")
async def get_training(
    training_uuid: UUID4,
    service: TrainingsService = Depends(get_trainings_service)
):
    training = await service.get_training(training_uuid)
    if not training:
        return JSONResponse(
            status_code=200,
            content={"detail": "Нет тренингов"}
        )
    return training


@router.get("/my_trainings/", response_model=list[TrainingListResponse], name="Получение всех тренингов пользователя")
async def get_my_trainings(
        token: str = Depends(oauth2_scheme),
        user_service: UserService = Depends(get_user_service),
        training_service: TrainingsService = Depends(get_trainings_service)
):
    user = await user_service.get_current_user(token)
    trainings = await training_service.get_trainings_by_user_id(user.id)

    if not trainings:
        return []
    return trainings


@router.patch("/{training_uuid}", name="Частичное обновление тренинга")
async def patch_training(
        training_uuid: UUID4,
        training_data: TrainingUpdate,
        token: str = Depends(oauth2_scheme),
        service: TrainingsService = Depends(get_trainings_service),
        user_service: UserService = Depends(get_user_service),
):
    """Частичное обновление тренинга и/или его шагов"""
    user = await user_service.get_current_user(token)

    # Обновление тренинга
    updated_training = await service.patch_training(training_uuid, training_data)

    return {
        "status": "success",
        "detail": "Данные тренинга успешно обновлены",
        "data": updated_training
    }



@router.delete("/{training_uuid}", name="Удаление тренинга по uuid")
async def delete_training(
    training_uuid: UUID4, service: TrainingsService = Depends(get_trainings_service)
):
    if await service.delete_training(training_uuid):
        return {"detail": "Тренинг успешно удален"}
    else:
        raise HTTPException(status_code=404, detail="Тренинг не найден")




@router.post("/upload-photos/{training_uuid}", name="Загрузка фото")
async def upload_photos_by_training(
        training_uuid: UUID4,
        files: List[UploadFile] = File(..., description="Загрузка фото"),
        s3_service: S3Service = Depends(get_s3_service),
        trainings_service: TrainingsService = Depends(get_trainings_service),
        token: str = Depends(oauth2_scheme),
):
    if not files:
        raise HTTPException(status_code=400, detail="Файлы не предоставлены")

    uploaded_urls = []

    for file in files:
        try:
            object_name = s3_service.generate_unique_filename(file.filename)
            file_content = await file.read()
            file_url = await s3_service.upload_file(file_content, object_name, training_uuid)
            uploaded_urls.append(file_url)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Ошибка загрузки файла {file.filename}: {str(e)}"
            )
        finally:
            await file.close()

    created_steps = await trainings_service.create_steps_from_photos(training_uuid, uploaded_urls)

    return {
        "success": True,
        "message": f"Загружено {len(uploaded_urls)} фотографий и создано {len(created_steps)} шагов тренинга",
        "uploaded_urls": uploaded_urls,
        "created_steps": created_steps
    }



# === ЭНДПОИНТЫ ДЛЯ УПРАВЛЕНИЯ ШАГАМИ ===

@router.post("/{training_uuid}/steps",
             response_model=TrainingStepResponse,
             name="Добавление шага к тренингу")
async def add_step(
    training_uuid: UUID4,
    step_data: TrainingStepCreate,
    token: str = Depends(oauth2_scheme),
    service: TrainingsService = Depends(get_trainings_service),
    user_service: UserService = Depends(get_user_service),
):
    """Добавление одного шага к тренингу"""
    user = await user_service.get_current_user(token)
    step = await service.add_step(training_uuid, step_data)
    return step


@router.post("/{training_uuid}/steps/bulk",
             response_model=List[TrainingStepResponse],
             name="Массовое добавление шагов")
async def add_steps_bulk(
    training_uuid: UUID4,
    request: StepBulkCreateRequest,
    token: str = Depends(oauth2_scheme),
    service: TrainingsService = Depends(get_trainings_service),
    user_service: UserService = Depends(get_user_service),
):
    """Массовое добавление шагов к тренингу"""
    user = await user_service.get_current_user(token)
    steps = await service.add_steps_bulk(training_uuid, request.steps)
    return steps



@router.patch(
    "/{training_uuid}/steps/{step_id}",
    response_model=TrainingStepResponse,
    summary="Обновить шаг тренинга"
)
async def update_training_step(
    training_uuid: UUID4,
    step_id: int,
    step_data: TrainingStepUpdate,
    service: TrainingsService = Depends(get_trainings_service)
):
    """Обновление шага по UUID тренинга и ID шага"""
    return await service.update_step(training_uuid, step_id, step_data)


@router.delete(
    "/{training_uuid}/steps/{step_id}",
    summary="Удалить шаг тренинга"
)
async def delete_training_step(
    training_uuid: UUID4,
    step_id: int,
    service: TrainingsService = Depends(get_trainings_service)
):
    """Удаление шага по UUID тренинга и ID шага"""
    await service.delete_step(training_uuid, step_id)
    return {"message": f"Шаг {step_id} успешно удалён"}


@router.delete(
    "/{training_uuid}/steps",
    summary="Массовое удаление шагов"
)
async def delete_training_steps_bulk(
    training_uuid: UUID4,
    step_ids: List[int],
    service: TrainingsService = Depends(get_trainings_service)
):
    """Массовое удаление шагов по UUID тренинга и списку ID"""
    result = await service.delete_steps_bulk(training_uuid, step_ids)
    return result


@router.get("/{training_uuid}/steps",
            response_model=List[TrainingStepResponse],
            name="Получение всех шагов тренинга")
async def get_training_steps(
    training_uuid: UUID4,
    service: TrainingsService = Depends(get_trainings_service),
):
    """Получение всех шагов тренинга"""
    steps = await service.get_training_steps(training_uuid)
    return [TrainingStepResponse.model_validate(step) for step in steps]


