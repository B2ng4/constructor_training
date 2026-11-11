"""Фоновая обработка видео для создания шагов тренинга."""

import asyncio
import os
import tempfile
from uuid import UUID

from core.logging_config import logger
from core.redis_pubsub import publish_task_notification
from models.tasks import TaskStatus, TaskType
from schemas.tasks import TaskNotificationPayload
from services.external_services.s3_service import S3Service
from services.trainings_service import TrainingsService
from services.video_ai_service import VideoAIService
from worker.task_runtime import get_worker_session_factory
from worker.db import _get_task_async, _update_task_async


def _analyze_video_blocking(video_ai: VideoAIService, video_path: str):
    """Тяжёлый AI/FFmpeg в отдельном потоке — не блокирует event loop worker."""
    return asyncio.run(video_ai.analyze_video_path(video_path))


def _notify_task(task, status: str, **kwargs) -> None:
    training_uuid = None
    if task and task.training_uuid:
        training_uuid = str(task.training_uuid)
    payload = TaskNotificationPayload(
        type="task_update",
        task_id=str(task.id) if task else kwargs.get("task_id", ""),
        status=status,
        progress=kwargs.get("progress", 0),
        result_url=kwargs.get("result_url"),
        error_message=kwargs.get("error_message"),
        message=kwargs.get("message"),
        training_uuid=training_uuid or kwargs.get("training_uuid"),
        steps_created=kwargs.get("steps_created"),
        task_type=TaskType.VIDEO_PROCESSING.value,
    )
    publish_task_notification(task.user_id, payload)


async def _task_still_active(task_id: str) -> bool:
    """Задача могла быть отменена пользователем (status=failed) во время обработки."""
    fresh = await _get_task_async(UUID(task_id))
    if not fresh:
        return False
    return fresh.status in (TaskStatus.PENDING.value, TaskStatus.PROCESSING.value)


async def _run_training_video_async(task_id: str) -> dict:
    task = await _get_task_async(UUID(task_id))
    if not task or not task.training_uuid:
        logger.error("Задача {} не найдена или без training_uuid", task_id)
        return {"ok": False, "error": "invalid_task"}

    if task.status in (TaskStatus.FAILED.value, TaskStatus.COMPLETED.value):
        logger.info("Задача {} уже в статусе {}, пропуск", task_id, task.status)
        return {"ok": False, "error": "task_not_active"}

    training_uuid = task.training_uuid
    user_id = task.user_id
    video_path: str | None = None
    training_title = "Тренинг"

    try:
        await _update_task_async(UUID(task_id), TaskStatus.PROCESSING.value, progress=5)
        _notify_task(
            task,
            TaskStatus.PROCESSING.value,
            progress=5,
            message="Начата обработка видео для тренинга",
        )

        s3 = S3Service(session=None)  # type: ignore[arg-type]
        object_key = S3Service.key_from_public_url(
            task.file_url, s3.bucket_name, s3.endpoint_url
        )

        await _update_task_async(
            UUID(task_id), TaskStatus.PROCESSING.value, progress=15
        )
        _notify_task(
            task,
            TaskStatus.PROCESSING.value,
            progress=15,
            message="Загрузка видео, подготовка к AI-анализу",
        )

        file_bytes = s3.download_bytes_sync(object_key)
        suffix = ".mp4"
        if task.original_filename and "." in task.original_filename:
            suffix = "." + task.original_filename.rsplit(".", 1)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            video_path = tmp.name

        await _update_task_async(
            UUID(task_id), TaskStatus.PROCESSING.value, progress=25
        )
        _notify_task(
            task,
            TaskStatus.PROCESSING.value,
            progress=25,
            message="AI анализирует видео — это может занять несколько минут",
        )

        session_factory = get_worker_session_factory()
        async with session_factory() as session:
            trainings_service = TrainingsService(session)
            try:
                training = await trainings_service.get_training_by_uuid(training_uuid)
                if training:
                    training_title = training.title
            except Exception:
                pass

        video_ai = VideoAIService()
        ai_steps = await asyncio.to_thread(
            _analyze_video_blocking, video_ai, video_path
        )

        # Пользователь мог отменить задачу, пока шёл AI-анализ — не пишем шаги.
        if not await _task_still_active(task_id):
            logger.info("Задача {} отменена во время анализа, шаги не создаются", task_id)
            return {"ok": False, "error": "cancelled"}

        await _update_task_async(
            UUID(task_id), TaskStatus.PROCESSING.value, progress=70
        )
        _notify_task(
            task,
            TaskStatus.PROCESSING.value,
            progress=70,
            message="Создание шагов тренинга",
        )

        async with session_factory() as session:
            from utils.pg_sequences import sync_training_steps_id_sequence

            await sync_training_steps_id_sequence(session)
            await session.commit()

        async with session_factory() as session:
            trainings_service = TrainingsService(session)
            created = await trainings_service.create_steps_from_ai_steps(
                training_uuid=training_uuid,
                ai_steps=ai_steps,
                s3_service=s3,
                creator_id=user_id,
            )

        steps_count = len(created)

        # Отмена могла прийти во время записи шагов — не перезаписываем статус.
        if not await _task_still_active(task_id):
            logger.info("Задача {} отменена во время создания шагов", task_id)
            return {"ok": False, "error": "cancelled"}

        await _update_task_async(
            UUID(task_id),
            TaskStatus.COMPLETED.value,
            progress=100,
            steps_created=steps_count,
        )
        _notify_task(
            task,
            TaskStatus.COMPLETED.value,
            progress=100,
            steps_created=steps_count,
            message=f"Тренинг «{training_title}» готов! Создано шагов: {steps_count}.",
        )
        return {
            "ok": True,
            "task_id": task_id,
            "steps_created": steps_count,
            "training_uuid": str(training_uuid),
        }

    except Exception as exc:
        logger.exception("Ошибка фоновой обработки видео {}", task_id)
        await _update_task_async(
            UUID(task_id),
            TaskStatus.FAILED.value,
            error_message=str(exc),
            progress=0,
        )
        task = await _get_task_async(UUID(task_id)) or task
        if task:
            _notify_task(
                task,
                TaskStatus.FAILED.value,
                error_message=str(exc),
                message="Не удалось создать шаги из видео",
            )
        raise

    finally:
        if video_path and os.path.exists(video_path):
            try:
                os.unlink(video_path)
            except OSError:
                pass
