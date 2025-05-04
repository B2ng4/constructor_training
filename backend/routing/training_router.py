from typing import List

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4

from depends import get_trainings_service, get_s3_service, get_user_service, get_photo_service
from starlette import status

from services.photo_service import PhotoService
from services.trainings_service import TrainingsService
from services.external_services.s3_service import S3Service
from schemas.trainings import TrainingResponse, TrainingUpdate, TrainingCreate
from services.user_service import UserService

router = APIRouter(prefix="/training", tags=["Тренинги"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse

@router.post("/create_training")
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





@router.get("/{training_uuid}", response_model=TrainingResponse)

async def get_training(training_uuid: UUID4, service: TrainingsService = Depends(get_trainings_service)):

    training = await service.get_training(training_uuid)
    if not training:
        raise HTTPException(status_code=404, detail="Тренинг не найден")
    return training



@router.get("/my_trainings/", response_model=list[TrainingResponse])
async def get_my_trainings(token: str = Depends(oauth2_scheme),
                           user_service: UserService = Depends(get_user_service),
                           training_service: TrainingsService = Depends(get_trainings_service)):
    user = await user_service.get_current_user(token)
    trainings = await training_service.get_trainings_by_user_id(user.id)
    if not trainings:
        raise HTTPException(status_code=404, detail="Тренинги не найдены")
    return trainings



@router.put("/{training_id}")
async def update_training(
    training_id: int,
    training_data: TrainingUpdate,
    service: TrainingsService = Depends(get_trainings_service),
):
    training = await service.update_training(training_id, training_data)
    if not training:
        raise HTTPException(status_code=404, detail="Тренинг не найден")

    return HTTPException(status_code=200, detail="Данные тренинга успешно обновлены")



@router.delete("/{training_uuid}")
async def delete_training(
    training_uuid: UUID4, service: TrainingsService = Depends(get_trainings_service)
):
    if await service.delete_training(training_uuid):
        return HTTPException(status.HTTP_200_OK, detail="Тренинг успешно удален")
    else:
        raise HTTPException(status_code=404, detail="Тренинг не найден")


# TODO: Добавить доступ к апихам по ролям, добавить ручки для получения тренингов по типу(фильтрация)


@router.post("/upload-photos/{training_uuid}")
async def upload_photos_by_training(
    training_uuid: UUID4,
    files: List[UploadFile] = File(..., description="Загрузка фото"),
    s3_service: S3Service = Depends(get_s3_service),
    token: str = Depends(oauth2_scheme),
):
    uploaded_urls = []
    for file in files:
        try:
            object_name = s3_service.generate_unique_filename(file.filename)
            file_content = await file.read()
            # Добавляем await здесь
            file_url = await s3_service.upload_file(file_content, object_name, training_uuid)
            uploaded_urls.append(file_url)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Ошибка загрузки файла: {str(e)}"
            )
        finally:
            await file.close()
    return {"uploaded_urls": uploaded_urls}


@router.get("/get_photos/{training_uuid}")
async def get_photos_by_training(
        training_uuid: UUID4,
        photo_service: PhotoService = Depends(get_photo_service),
        token: str = Depends(oauth2_scheme),
):
    try:
        photo_urls = await photo_service.get_all_photos(training_uuid)
        if not photo_urls:
            raise HTTPException(
                status_code=404,
                detail=f"Фотографии для тренировки с ID {training_uuid} не найдены"
            )
        training_photo_urls = {
            str(i + 1): url for i, url in enumerate(photo_urls)
        }
        return {"training_photos": training_photo_urls}
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Тренировка с ID {training_uuid} не найдена"
        )
