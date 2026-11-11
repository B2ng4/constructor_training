from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from core.database import engine, get_async_session
from core.logging_config import logger
from repositories.users_repository import UserRepository
from scripts.create_initial_actions import create_initial_actions
from scripts.create_initial_levels import create_initial_levels
from scripts.create_initial_tags import create_initial_tags
from scripts.create_user import create_test_user
from services.temp_employee_accounts_service import TempEmployeeAccountsService
from utils.pg_sequences import sync_training_steps_id_sequence


async def create_initial_user(enabled: bool):
    """Создаёт тестового пользователя при первом запуске (только по флагу SEED_TEST_USER)"""
    if not enabled:
        return
    async for session in get_async_session():
        repo = UserRepository(session)
        if await repo.count_users() == 0:
            await create_test_user()


def create_base_app(configs):
    io_executor = ThreadPoolExecutor(max_workers=32, thread_name_prefix="api-io")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
        """Управление жизненным циклом приложения."""
        loop = asyncio.get_running_loop()
        loop.set_default_executor(io_executor)
        logger.info("Инициализация приложения...")
        await create_initial_user(configs.SEED_TEST_USER)
        await create_initial_actions()
        await create_initial_tags()
        await create_initial_levels()
        async for session in get_async_session():
            await sync_training_steps_id_sequence(session)
            removed = await TempEmployeeAccountsService(session).cleanup_expired()
            if removed:
                logger.info("Removed {} expired temporary employee accounts on startup", removed)
            await session.commit()
            break
        yield
        io_executor.shutdown(wait=False, cancel_futures=True)
        await engine.dispose()
        logger.info("Завершение работы приложения...")

    app = FastAPI(
        title=configs.PROJECT_NAME,
        lifespan=lifespan,
        description=configs.PROJECT_DESCRIPTION,
    )

    cors_origins = [o.strip() for o in (configs.CORS_ORIGINS or "*").split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["*"],
        # credentials + "*" несовместимы; с Bearer-токенами куки не нужны
        allow_credentials="*" not in cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=HTMLResponse)
    def root():
        return """
        <html>
            <head>
                <title>Добро пожаловать</title>
                <style>
                    button {
                        padding: 10px 20px;
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }
                    button:hover {
                        background-color: #45a049;
                    }
                </style>
            </head>
            <body>
                <h1>Запустилось и работает!</h1>
                <a href="/docs">
                    <button>Перейти к документации</button>
                </a>
            </body>
        </html>
        """

    return app
