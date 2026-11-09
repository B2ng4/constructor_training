import os
import sys

# Ensure backend root is discoverable for Celery imports.
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from celery import Celery

from core.config import configs

_IS_WINDOWS = sys.platform == "win32"

celery_app = Celery(
    "events_knastu",
    broker=configs.CELERY_BROKER_URL,
    backend=configs.CELERY_RESULT_BACKEND,
    include=["worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_concurrency=1,
    beat_schedule={
        "cleanup-expired-employee-accounts": {
            "task": "worker.tasks.cleanup_expired_employee_accounts",
            "schedule": 3600.0,
        },
    },
)
if _IS_WINDOWS:
    celery_app.conf.update(worker_pool="solo")

# Workaround для бага Celery 5.5.x: геттер `_backend` читает `self._local.app`,
# а сеттер пишет в `self._local.backend` — `app.backend` возвращает None для
# не-thread-safe бэкендов (Redis). Прогреваем кэш напрямую.
celery_app._backend_cache = celery_app._get_backend()
