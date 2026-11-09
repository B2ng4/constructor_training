# Запуск на сервере (Docker)

Полный стек: **frontend**, **backend (API)**, **celery_worker**, **PostgreSQL**, **Redis**.

## Быстрый старт

```bash
# 1. Конфиг — backend/.env (секреты, S3, AI, Yandex)
cp backend/.env.example backend/.env   # если файла ещё нет
nano backend/.env

# 2. Опционально: симлинк для подстановки POSTGRES_* в compose
ln -sf backend/.env .env

# 3. Сборка и запуск
docker compose up -d --build

# 4. Проверка
docker compose ps
docker compose logs -f backend
docker compose logs -f celery_worker
```

> Все переменные — в **`backend/.env`**. Корневой `.env` не обязателен (только симлинк для compose).

После старта:
- Сайт: `http://<хост>/` (frontend, порт 80)
- API: `http://<хост>:8001/` (backend, порт 8001)
- WebSocket уведомлений: `ws://<хост>:8001/ws/notifications`

> Фронт собирается с `VITE_API_BASE_URL` — URL API, зашитый в сборку (compose-значение по умолчанию `http://localhost:8001`). На сервере передайте свой URL через build-arg или настройте внешний reverse proxy (`/` → frontend, API → backend:8001).

## Сервисы

| Сервис | Назначение |
|--------|------------|
| `backend` | FastAPI (uvicorn :8001), миграции Alembic при старте |
| `celery_worker` | Фоновая обработка видео (AI + S3) |
| `redis` | Брокер Celery + pub/sub для WebSocket |
| `db` | PostgreSQL 15 |
| `frontend` | Статика Vue (`serve`, порт 80) |

## Celery worker

В Docker worker запускается автоматически сервисом `celery_worker`:

```bash
docker compose up -d celery_worker
docker compose logs -f celery_worker
docker compose restart celery_worker
```

Команда внутри контейнера (Linux, prefork, 1 процесс):

```bash
celery -A core.celery_app worker --loglevel=info --concurrency=1 --hostname=worker@%h
```

На Windows в dev используйте `-P solo -c 1` (см. `run_celery_worker.md`).

### Очистка зависших задач

```bash
docker compose exec celery_worker python scripts/cleanup_stuck_tasks.py
docker compose restart celery_worker
```

## Обновление после git pull

```bash
git pull
docker compose up -d --build
# миграции применяются при рестарте backend (alembic upgrade head)
```

## Локальная разработка без Docker

Два терминала + Redis локально:

**API:**
```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --host 0.0.0.0 --port 8002
```

**Worker:**
```bash
cd backend
uv run celery -A core.celery_app worker --loglevel=info -P solo -c 1   # Windows
# uv run celery -A core.celery_app worker --loglevel=info -c 1         # Linux/macOS
```

## Переменные окружения

Конфиг: **`backend/.env`**

| Переменные | Назначение |
|------------|------------|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | PostgreSQL (должны совпадать с `DB_*`) |
| `REDIS_URL`, `CELERY_*` | В Docker лучше `redis://redis:6379/0` |
| `SECRET_KEY`, `AWS_*`, `S3_*`, `AI_*` | Backend |
| `YANDEX_*`, `FRONTEND_PUBLIC_URL` | OAuth |

Compose переопределяет для Docker: `DB_HOST=db`, `DB_PASS` из `POSTGRES_PASSWORD`.

Опционально: `ln -sf backend/.env .env` — чтобы compose подставлял `${POSTGRES_*}` из вашего файла.

**Важно:** `POSTGRES_PASSWORD` = пароль при создании volume `postgres_data` (обычно `admin`).

`DB_HOST=localhost` в `backend/.env` **игнорируется** — compose задаёт `DB_HOST=db`.

## Troubleshooting

**Видео загружается, но шаги не создаются**
- Проверьте worker: `docker compose logs celery_worker`
- Redis: `docker compose exec redis redis-cli ping` → `PONG`
- S3 и AI ключи в `backend/.env`

**API или WebSocket недоступны**

**Backend недоступен**. Проверьте:

```bash
docker compose ps
docker compose logs backend --tail 50
curl -s http://localhost:8001/ || echo "backend unreachable"
```

Если backend `Restarting` или `unhealthy` — сначала почините БД (см. выше `InvalidPasswordError`):

```bash
grep '^DB_' backend/.env
docker compose exec db psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'ВАШ_DB_PASS';"
docker compose up -d --build backend celery_worker frontend
```

Когда backend `healthy`, API и `ws://<хост>:8001/ws/notifications` заработают.


**Worker падает при второй задаче (только dev на Windows)**
- Используйте `-P solo -c 1`; в Docker (Linux) это не требуется

**Backend unhealthy / Restarting (1)**

```bash
docker compose logs backend --tail 80
```

Частые причины:

1. **Пароль PostgreSQL не совпадает** — volume `postgres_data` хранит старый пароль. Если в `.env` сменили `POSTGRES_PASSWORD`, БД всё равно использует пароль при первом создании volume.

   ```bash
   grep POSTGRES_PASSWORD backend/.env
   grep DB_PASS backend/.env
   ```

   Пароль в `.env` (`POSTGRES_PASSWORD`) должен совпадать с тем, с которым volume был создан (раньше часто `admin`). Либо верните `POSTGRES_PASSWORD=admin`, либо пересоздайте volume (удалит данные!):

   ```bash
   docker compose down
   docker volume rm constructor_training_postgres_data
   docker compose up -d --build
   ```

2. **`backend/.env` переопределяет хост БД** — в Docker не задавайте `DB_HOST=localhost` в `backend/.env`. Хост задаёт `docker-compose.yml` (`DB_HOST=db`).

3. **Ошибка миграции Alembic** — в логах будет `alembic upgrade head`. Ручной прогон:

   ```bash
   docker compose run --rm backend alembic upgrade head
   ```

Для отладки БД/Redis с хоста добавьте в `docker-compose.yml` проброс портов `5432` / `6379`.
