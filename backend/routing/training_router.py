from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from core.config import public_passage_link
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import UUID4

from depends import (
    get_current_creator,
    get_current_user,
    get_gigachat_tts_service,
    get_s3_service,
    get_trainings_service,
    get_video_ai_service,
)
from models.users import User
from utils.upload_validation import (
    IMAGE_EXTENSIONS,
    MAX_ICON_BYTES,
    MAX_IMAGE_BYTES,
    MAX_PDF_BYTES,
    MAX_VIDEO_BYTES,
    PDF_EXTENSIONS,
    VIDEO_EXTENSIONS,
    check_declared_size,
    check_extension,
    read_limited,
)
from schemas.trainings import (
    PassageAnalyticsResponse,
    PassageCompleteRequest,
    PassageHistoryItemResponse,
    ScenarioGraphResponse,
    ScenarioGraphUpdate,
    StepBulkCreateRequest,
    StepsReorderRequest,
    TrainingCreate,
    TrainingListResponse,
    TrainingResponse,
    TrainingStepCreate,
    TrainingStepResponse,
    TrainingStepUpdate,
    TrainingUpdate,
    TextRewriteRequest,
    TextRewriteResponse,
)
from schemas.users import UserRole
from services.external_services.gigachat_tts_service import GigaChatTTSService
from services.external_services.s3_service import S3Service
from services.pdf_ai_service import PdfAiService
from services.trainings_service import TrainingsService
from services.video_ai_service import VideoAIService

router = APIRouter(prefix="/training", tags=["Тренинги"])

MAX_PHOTO_FILES_PER_REQUEST = 50


@router.post("/create_training", name="Создание тренинга")
async def create_training(
    ser_data: TrainingCreate,
    training_service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    """Создание нового тренинга"""
    created_training = await training_service.create_training(ser_data, user.id)

    if created_training:
        return {"status": status.HTTP_201_CREATED, "data": created_training.dict()}
    else:
        raise HTTPException(status_code=404, detail="Тренинг не создан")


@router.get("/{training_uuid}", name="Получение конкретного тренинга")
async def get_training(
    training_uuid: UUID4,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_user),
):
    training = await service.get_training(training_uuid)
    if not training:
        raise HTTPException(status_code=404, detail="Тренинг не найден")
    if not training.publish and training.creator_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому тренингу")
    return training


@router.get(
    "/my_trainings/",
    response_model=list[TrainingListResponse],
    name="Получение всех тренингов пользователя",
)
async def get_my_trainings(
    user: User = Depends(get_current_user),
    training_service: TrainingsService = Depends(get_trainings_service),
):
    if user.role == UserRole.EMPLOYEE:
        return []
    trainings = await training_service.get_trainings_by_user_id(user.id)

    if not trainings:
        return []
    return trainings


@router.patch("/{training_uuid}", name="Частичное обновление тренинга")
async def patch_training(
    training_uuid: UUID4,
    training_data: TrainingUpdate,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    """Частичное обновление тренинга и/или его шагов"""
    await service._require_training_owner(training_uuid, user.id)
    updated_training = await service.patch_training(training_uuid, training_data)

    return {
        "status": "success",
        "detail": "Данные тренинга успешно обновлены",
        "data": updated_training,
    }


@router.delete("/{training_uuid}", name="Удаление тренинга по uuid")
async def delete_training(
    training_uuid: UUID4,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    await service._require_training_owner(training_uuid, user.id)
    if await service.delete_training(training_uuid):
        return {"detail": "Тренинг успешно удален"}
    else:
        raise HTTPException(status_code=404, detail="Тренинг не найден")


@router.post("/upload-icon/{training_uuid}", name="Загрузка иконки тренинга")
async def upload_icon_for_training(
    training_uuid: UUID4,
    file: UploadFile = File(...),
    s3_service: S3Service = Depends(get_s3_service),
    trainings_service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    await trainings_service._require_training_owner(training_uuid, user.id)

    check_extension(file.filename, IMAGE_EXTENSIONS, "иконки")
    content = await read_limited(file, MAX_ICON_BYTES, "Иконка")

    object_name = s3_service.generate_unique_filename(file.filename)
    file_url = await s3_service.upload_file(content, object_name, training_uuid)

    # Обновляем тренинг
    await trainings_service.patch_training(training_uuid, TrainingUpdate(icon=file_url))

    return {"success": True, "icon_url": file_url}


@router.post("/upload-photos/{training_uuid}", name="Загрузка фото")
async def upload_photos_by_training(
    training_uuid: UUID4,
    files: List[UploadFile] = File(..., description="Загрузка фото"),
    detect_ui_elements: bool = Query(True, description="Запустить YOLO-детекцию UI-элементов после загрузки"),
    s3_service: S3Service = Depends(get_s3_service),
    trainings_service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    if not files:
        raise HTTPException(status_code=400, detail="Файлы не предоставлены")
    if len(files) > MAX_PHOTO_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"За один раз можно загрузить не более {MAX_PHOTO_FILES_PER_REQUEST} файлов",
        )

    await trainings_service._require_training_owner(training_uuid, user.id)

    uploaded_urls = []

    for file in files:
        try:
            check_extension(file.filename, IMAGE_EXTENSIONS, "изображения")
            object_name = s3_service.generate_unique_filename(file.filename)
            file_content = await read_limited(file, MAX_IMAGE_BYTES, "Изображение")
            file_url = await s3_service.upload_file(
                file_content, object_name, training_uuid
            )
            uploaded_urls.append(file_url)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка загрузки файла {file.filename}: {str(e)}",
            )
        finally:
            await file.close()

    created_steps = await trainings_service.create_steps_from_photos(
        training_uuid, uploaded_urls, detect_ui_elements=detect_ui_elements
    )

    return {
        "success": True,
        "message": f"Загружено {len(uploaded_urls)} фотографий и создано {len(created_steps)} шагов тренинга",
        "uploaded_urls": uploaded_urls,
        "created_steps": created_steps,
    }


@router.post(
    "/upload-video/{training_uuid}",
    name="Загрузка видео (AI-анализ, фоновая очередь)",
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_video_for_training_async(
    training_uuid: UUID4,
    file: UploadFile = File(..., description="Видеофайл"),
    s3_service: S3Service = Depends(get_s3_service),
    trainings_service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    check_extension(file.filename, VIDEO_EXTENSIONS, "видео")
    check_declared_size(file, MAX_VIDEO_BYTES, "Видео")
    result = await trainings_service.start_async_video_processing(
        training_uuid=training_uuid,
        user_id=user.id,
        video_file=file,
        s3_service=s3_service,
    )
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=result.model_dump(mode="json"),
    )


# === ЭНДПОИНТЫ ДЛЯ УПРАВЛЕНИЯ ШАГАМИ ===


@router.post(
    "/{training_uuid}/steps",
    response_model=TrainingStepResponse,
    name="Добавление шага к тренингу",
)
async def add_step(
    training_uuid: UUID4,
    step_data: TrainingStepCreate,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    """Добавление одного шага к тренингу"""
    await service._require_training_owner(training_uuid, user.id)
    step = await service.add_step(training_uuid, step_data)
    return step


@router.post(
    "/{training_uuid}/steps/bulk",
    response_model=List[TrainingStepResponse],
    name="Массовое добавление шагов",
)
async def add_steps_bulk(
    training_uuid: UUID4,
    request: StepBulkCreateRequest,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    """Массовое добавление шагов к тренингу"""
    await service._require_training_owner(training_uuid, user.id)
    steps = await service.add_steps_bulk(training_uuid, request.steps)
    return steps


@router.patch(
    "/{training_uuid}/steps/reorder",
    summary="Обновить порядок шагов в тренинге",
    name="Обновление порядка шагов",
)
async def reorder_training_steps(
    training_uuid: UUID4,
    request: StepsReorderRequest,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    await service._require_training_owner(training_uuid, user.id)
    """
    Эндпойнт для массового обновления порядковых номеров (step_number)
    шагов в тренинге.
    """
    result = await service.reorder_steps(training_uuid, request.steps)
    return {
        "status": "success",
        "detail": "Порядок шагов успешно обновлен",
        "data": result,
    }


@router.patch(
    "/{training_uuid}/steps/{step_id}",
    response_model=TrainingStepResponse,
    summary="Обновить шаг тренинга",
)
async def update_training_step(
    training_uuid: UUID4,
    step_id: int,
    step_data: TrainingStepUpdate,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    """Обновление шага по UUID тренинга и ID шага"""
    await service._require_training_owner(training_uuid, user.id)
    return await service.update_step(training_uuid, step_id, step_data)


@router.get(
    "/{training_uuid}/steps/{step_id}/screenshot-source",
    name="Скриншот шага для редактора (без CORS S3)",
)
async def get_step_screenshot_source(
    training_uuid: UUID4,
    step_id: int,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
    s3_service: S3Service = Depends(get_s3_service),
):
    content, media_type = await service.get_step_screenshot_bytes(
        training_uuid, step_id, user.id, s3_service
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Cache-Control": "private, max-age=60"},
    )


@router.post(
    "/{training_uuid}/steps/{step_id}/screenshot",
    response_model=TrainingStepResponse,
    name="Заменить скриншот шага",
)
async def replace_step_screenshot(
    training_uuid: UUID4,
    step_id: int,
    file: UploadFile = File(...),
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
    s3_service: S3Service = Depends(get_s3_service),
):
    check_extension(file.filename, IMAGE_EXTENSIONS, "скриншота")
    content = await read_limited(file, MAX_IMAGE_BYTES, "Скриншот")
    try:
        return await service.replace_step_screenshot(
            training_uuid,
            step_id,
            user.id,
            content,
            file.filename or "screenshot.png",
            s3_service,
        )
    finally:
        await file.close()


@router.post(
    "/{training_uuid}/steps/{step_id}/detect-elements",
    response_model=TrainingStepResponse,
    name="Детекция UI-элементов на скриншоте шага (YOLO)",
)
async def detect_step_ui_elements(
    training_uuid: UUID4,
    step_id: int,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
    s3_service: S3Service = Depends(get_s3_service),
):
    return await service.detect_step_ui_elements(
        training_uuid, step_id, user.id, s3_service
    )


@router.delete("/{training_uuid}/steps/{step_id}", summary="Удалить шаг тренинга")
async def delete_training_step(
    training_uuid: UUID4,
    step_id: int,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    """Удаление шага по UUID тренинга и ID шага"""
    await service._require_training_owner(training_uuid, user.id)
    await service.delete_step(training_uuid, step_id)
    return {"message": f"Шаг {step_id} успешно удалён"}


@router.delete("/{training_uuid}/steps", summary="Массовое удаление шагов")
async def delete_training_steps_bulk(
    training_uuid: UUID4,
    step_ids: List[int],
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    """Массовое удаление шагов по UUID тренинга и списку ID"""
    await service._require_training_owner(training_uuid, user.id)
    result = await service.delete_steps_bulk(training_uuid, step_ids)
    return result


@router.get(
    "/{training_uuid}/steps",
    response_model=List[TrainingStepResponse],
    name="Получение всех шагов тренинга",
)
async def get_training_steps(
    training_uuid: UUID4,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_user),
):
    """Получение всех шагов тренинга"""
    training = await service.repo.get_by_uuid(training_uuid)
    if not training:
        raise HTTPException(status_code=404, detail="Тренинг не найден")
    if not training.publish and training.creator_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому тренингу")
    steps = await service.get_training_steps(training_uuid)
    return [TrainingStepResponse.model_validate(step) for step in steps]


@router.get(
    "/{training_uuid}/scenario",
    response_model=ScenarioGraphResponse,
    name="Получить сценарный граф тренинга",
)
async def get_scenario_graph(
    training_uuid: UUID4,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    await service._require_training_owner(training_uuid, user.id)
    return await service.get_scenario_graph(training_uuid)


@router.put(
    "/{training_uuid}/scenario",
    response_model=ScenarioGraphResponse,
    name="Сохранить сценарный граф тренинга",
)
async def update_scenario_graph(
    training_uuid: UUID4,
    graph: ScenarioGraphUpdate,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    return await service.update_scenario_graph(training_uuid, graph, user.id)


@router.post("/{training_uuid}/publish", name="Опубликовать тренинг")
async def publish_training(
    training_uuid: UUID4,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    await service._require_training_owner(training_uuid, user.id)
    token = await service.publish_training(training_uuid)
    return {
        "success": True,
        "public_link": public_passage_link(token),
        "access_token": token,
    }


@router.post("/{training_uuid}/unpublish", name="Снять тренинг с публикации")
async def unpublish_training(
    training_uuid: UUID4,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    await service._require_training_owner(training_uuid, user.id)
    await service.unpublish_training(training_uuid)
    return {"success": True, "message": "Тренинг снят с публикации"}


@router.post(
    "/public/{access_token}/passage/start",
    name="Начать анонимную попытку прохождения",
)
async def start_passage_attempt(
    access_token: str,
    service: TrainingsService = Depends(get_trainings_service),
):
    return await service.start_public_passage_attempt(access_token)


@router.post(
    "/public/{access_token}/passage/complete",
    name="Завершить попытку прохождения",
)
async def complete_passage_attempt(
    access_token: str,
    body: PassageCompleteRequest,
    service: TrainingsService = Depends(get_trainings_service),
):
    return await service.complete_public_passage_attempt(access_token, body)


@router.get(
    "/{training_uuid}/passage-analytics",
    response_model=PassageAnalyticsResponse,
    name="Статистика прохождений (автор)",
)
async def get_passage_analytics(
    training_uuid: UUID4,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    return await service.get_passage_analytics_for_creator(training_uuid, user.id)


@router.get(
    "/{training_uuid}/passage-history",
    response_model=list[PassageHistoryItemResponse],
    name="История прохождений (автор)",
)
async def get_passage_history(
    training_uuid: UUID4,
    skip: int = 0,
    limit: int = 20,
    service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    return await service.get_passage_history_for_creator(
        training_uuid, user.id, skip=skip, limit=limit
    )


@router.get("/public/{access_token}", name="Получить публичный тренинг")
async def get_public_training(
    access_token: str, service: TrainingsService = Depends(get_trainings_service)
):
    return await service.get_public_training_data(access_token)


@router.post(
    "/ai/rewrite-task",
    name="AI-улучшение текста задания",
)
async def ai_rewrite_task(
    request: TextRewriteRequest,
    video_ai_service: VideoAIService = Depends(get_video_ai_service),
    user: User = Depends(get_current_creator),
):
    try:

        def stream_generator():
            for chunk in video_ai_service.stream_rewrite_task_text(request.text):
                yield chunk

        return StreamingResponse(stream_generator(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка переписывания текста: {str(e)}"
        )


@router.post(
    "/{training_uuid}/steps/{step_id}/tts",
    name="Генерация озвучки для шага",
)
async def generate_step_tts(
    training_uuid: UUID4,
    step_id: int,
    tts_service: GigaChatTTSService = Depends(get_gigachat_tts_service),
    s3_service: S3Service = Depends(get_s3_service),
    training_service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    """Генерация аудиофайла для задания шага через SaluteSpeech и сохранение в S3"""
    import traceback
    import uuid as uuid_lib
    from core.logging_config import logger

    try:
        await training_service._require_training_owner(training_uuid, user.id)

        # Получаем шаг из БД
        steps = await training_service.get_training_steps(training_uuid)
        step = next((s for s in steps if s.id == step_id), None)
        if not step:
            raise HTTPException(status_code=404, detail="Шаг не найден")

        annotation = step.annotation
        if not annotation or not annotation.strip():
            raise HTTPException(status_code=400, detail="Текст задания пустой")

        # Синтезируем речь
        logger.info(f"[TTS] Запрос синтеза речи для шага {step_id}")
        audio_bytes = await tts_service.synthesize(annotation)
        logger.info(f"[TTS] Синтез завершён, получено {len(audio_bytes)} байт")

        # Загружаем в S3
        object_name = f"audio/{uuid_lib.uuid4()}.wav"
        audio_url = await s3_service.upload_file(
            audio_bytes, object_name, training_uuid
        )
        logger.info(f"[TTS] Аудио сохранено в S3: {audio_url}")

        # Сохраняем audio_url в БД
        await training_service.update_step(
            training_uuid, step_id, TrainingStepUpdate(audio_url=audio_url)
        )

        return {"audio_url": audio_url}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TTS] Ошибка: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Ошибка генерации озвучки: {str(e)}"
        )


@router.post("/upload-pdf/{training_uuid}", name="Загрузка PDF-инструкции (AI-анализ)")
async def upload_pdf_for_training(
    training_uuid: UUID4,
    file: UploadFile = File(..., description="PDF-файл инструкции"),
    s3_service: S3Service = Depends(get_s3_service),
    trainings_service: TrainingsService = Depends(get_trainings_service),
    user: User = Depends(get_current_creator),
):
    """
    Принимает PDF-инструкцию и ставит задачу на анализ каждой страницы через VLM в очередь.
    Возвращает ID задачи для отслеживания.
    """
    check_extension(file.filename, PDF_EXTENSIONS, "инструкции")
    pdf_bytes = await read_limited(file, MAX_PDF_BYTES, "PDF")

    # Save to S3 for background worker
    from models.tasks import TaskType
    from repositories.tasks_repository import TasksRepository
    from core.task_queue import enqueue_process_training_pdf
    import asyncio

    # Ensure training exists and user is owner
    await trainings_service._require_training_owner(training_uuid, user.id)

    # upload bytes to S3
    object_key = s3_service.generate_task_object_key(
        user.id, file.filename, prefix="pdf_uploads"
    )
    file_url = await s3_service.upload_file(pdf_bytes, object_key, training_uuid)

    tasks_repo = TasksRepository(trainings_service.session)
    task = await tasks_repo.create(
        user_id=user.id,
        task_type=TaskType.PDF_PROCESSING.value,
        status="pending",
        original_filename=file.filename,
        file_url=file_url,
        training_uuid=training_uuid,
    )

    await asyncio.to_thread(enqueue_process_training_pdf, str(task.id))

    return {
        "success": True,
        "message": "PDF загружен и поставлен в очередь на обработку",
        "task_id": str(task.id)
    }
