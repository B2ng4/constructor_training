"""Celery-клиент"""

from celery import Celery

from core.config import configs

_publisher: Celery | None = None


def get_task_publisher() -> Celery:
    global _publisher
    if _publisher is None:
        _publisher = Celery(
            "events_knastu_publisher",
            broker=configs.CELERY_BROKER_URL,
            backend=configs.CELERY_RESULT_BACKEND,
        )
        _publisher.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
        )
        # Workaround для бага Celery 5.5.x: геттер `_backend` читает
        # `self._local.app`, а сеттер пишет в `self._local.backend`, поэтому
        # `app.backend` возвращает None для не-thread-safe бэкендов (Redis)
        # и send_task падает с AttributeError. Прогреваем кэш напрямую.
        _publisher._backend_cache = _publisher._get_backend()
    return _publisher


def enqueue_process_training_video(task_id: str) -> None:
    get_task_publisher().send_task(
        "worker.tasks.process_training_video_task",
        args=[task_id],
    )

def enqueue_process_training_pdf(task_id: str) -> None:
    get_task_publisher().send_task(
        "worker.tasks.process_training_pdf_task",
        args=[task_id],
    )
