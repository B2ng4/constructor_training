import asyncio
from uuid import UUID

from loguru import logger

from core.redis_pubsub import publish_task_notification
from models.tasks import TaskStatus, TaskType
from schemas.tasks import TaskNotificationPayload
from services.external_services.s3_service import S3Service
from services.pdf_ai_service import PdfAiService
from services.trainings_service import TrainingsService
from worker.task_runtime import get_worker_session_factory
from worker.db import _get_task_async, _update_task_async


def _notify_task(task, status: str, **kwargs) -> None:
    if task and task.training_uuid:
        training_uuid = str(task.training_uuid)
        payload = TaskNotificationPayload(
            type="task_update",
            task_id=str(task.id) if task else kwargs.get("task_id", ""),
            status=status,
            progress=kwargs.get("progress", 0),
            error_message=kwargs.get("error_message"),
            result_url=kwargs.get("result_url"),
            training_uuid=training_uuid,
            steps_created=kwargs.get("steps_created"),
            task_type=TaskType.PDF_PROCESSING.value,
        )
        publish_task_notification(task.user_id, payload)


async def _task_still_active(task_id: str) -> bool:
    fresh = await _get_task_async(UUID(task_id))
    if not fresh:
        return False
    return fresh.status in (TaskStatus.PENDING.value, TaskStatus.PROCESSING.value)


async def _run_training_pdf_async(task_id: str) -> dict:
    task = await _get_task_async(UUID(task_id))
    if not task or not task.training_uuid:
        logger.error("Задача {} не найдена или без training_uuid", task_id)
        return {"ok": False, "error": "invalid_task"}

    if task.status in (TaskStatus.FAILED.value, TaskStatus.COMPLETED.value):
        logger.info("Задача {} уже в статусе {}, пропуск", task_id, task.status)
        return {"ok": False, "error": "task_not_active"}

    training_uuid = task.training_uuid
    user_id = task.user_id

    try:
        logger.info(f"Начинаем скачивание PDF для задачи {task_id}")
        await _update_task_async(UUID(task_id), TaskStatus.PROCESSING.value, progress=5)
        _notify_task(
            task,
            TaskStatus.PROCESSING.value,
            progress=5,
            message="Скачивание файла PDF...",
        )

        s3 = S3Service(session=None)  # type: ignore[arg-type]
        object_key = S3Service.key_from_public_url(
            task.file_url, s3.bucket_name, s3.endpoint_url
        )
        pdf_bytes = await asyncio.to_thread(s3.download_bytes_sync, object_key)
        
        if not pdf_bytes:
            raise ValueError("Не удалось скачать PDF-файл из S3")

        await _update_task_async(
            UUID(task_id), TaskStatus.PROCESSING.value, progress=15
        )
        _notify_task(
            task,
            TaskStatus.PROCESSING.value,
            progress=15,
            message="Анализ PDF через VLM...",
        )

        if not await _task_still_active(task_id):
            logger.info("Задача {} отменена до анализа, шаги не создаются", task_id)
            return {"ok": False, "error": "cancelled"}

        SessionFactory = get_worker_session_factory()
        async with SessionFactory() as session:
            pdf_ai = PdfAiService()
            trainings_service = TrainingsService(session)
            
            # This calls the service which already chunks the PDF pages and does VLM
            created_steps = await trainings_service.add_steps_from_pdf(
                training_uuid=training_uuid,
                pdf_bytes=pdf_bytes,
                pdf_ai_service=pdf_ai,
                s3_service=s3,
            )
            num_steps = len(created_steps)

        # Задача могла быть отменена, пока шёл анализ — не перезаписываем её статус.
        if not await _task_still_active(task_id):
            logger.info("Задача {} отменена во время анализа", task_id)
            return {"ok": False, "error": "cancelled"}

        await _update_task_async(
            UUID(task_id),
            TaskStatus.COMPLETED.value,
            progress=100,
            steps_created=num_steps,
        )
        task = await _get_task_async(UUID(task_id)) or task
        _notify_task(
            task,
            TaskStatus.COMPLETED.value,
            progress=100,
            steps_created=num_steps,
            message=f"PDF успешно обработан. Создано шагов: {num_steps}",
        )

        return {
            "ok": True,
            "task_id": task_id,
            "steps_created": num_steps,
        }

    except Exception as e:
        logger.exception("Ошибка фоновой обработки PDF {}", task_id)
        await _update_task_async(
            UUID(task_id),
            TaskStatus.FAILED.value,
            progress=0,
            error_message=str(e),
        )
        task = await _get_task_async(UUID(task_id)) or task
        if task:
            _notify_task(
                task,
                TaskStatus.FAILED.value,
                progress=0,
                error_message=str(e),
            )
        return {"ok": False, "error": str(e)}
