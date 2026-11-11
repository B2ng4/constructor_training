#!/bin/sh
set -e

echo "==> Инициализация базы данных..."
python init_db.py

# Если появятся миграции в alembic/versions — применяем их
if ls alembic/versions/*.py >/dev/null 2>&1; then
    echo "==> Применение миграций Alembic..."
    alembic upgrade head
fi

APP_HOST="${HOST:-0.0.0.0}"
APP_PORT="${PORT:-8001}"
echo "==> Запуск backend на ${APP_HOST}:${APP_PORT}"
exec uvicorn main:app --host "$APP_HOST" --port "$APP_PORT"
