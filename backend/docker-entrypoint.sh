#!/bin/sh
set -e

echo "==> Инициализация базы данных..."
python init_db.py

# Если появятся миграции в alembic/versions — применяем их
if [ -n "$(ls -A alembic/versions/*.py 2>/dev/null)" ]; then
    echo "==> Применение миграций Alembic..."
    alembic upgrade head
fi

echo "==> Запуск backend на :8001"
exec uvicorn main:app --host 0.0.0.0 --port 8001
