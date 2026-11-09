# Конструктор Тренингов (SkillSnap)

Веб-сервис для создания интерактивных тренингов по работе в ПО.

## Запуск на сервере (Docker)

```bash
nano backend/.env          # секреты, S3, AI, POSTGRES_PASSWORD=admin
ln -sf backend/.env .env   # опционально, для compose

docker compose up -d --build
docker compose logs -f backend
```

Полная инструкция: **[docs/DEPLOY.md](docs/DEPLOY.md)**

Стек: FastAPI + Celery + Redis + PostgreSQL + Vue.

## Локальная разработка

### Backend

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --host 0.0.0.0 --port 8002
```

### Celery worker (отдельный терминал)

```bash
cd backend
uv run celery -A core.celery_app worker --loglevel=info -P solo -c 1   # Windows
```

Подробнее: [backend/scripts/run_celery_worker.md](backend/scripts/run_celery_worker.md)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Стек

**Backend:** FastAPI, PostgreSQL, Redis, Celery, S3, Alembic  
**Frontend:** Vue 3, Vite, Quasar, Pinia
