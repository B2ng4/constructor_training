from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from starlette.responses import HTMLResponse

from core.database import get_async_session
from repositories.users_repository import UserRepository
from scripts.create_user import create_test_user


async def create_initial_user():
    """Создаёт тестового пользователя при первом запуске"""
    async for session in get_async_session():
        repo = UserRepository(session)
        if await repo.count_users() == 0:
            await create_test_user()


def create_base_app(configs):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
        """Управление жизненным циклом приложения."""
        logger.info("Инициализация приложения...")
        await create_initial_user()
        yield
        logger.info("Завершение работы приложения...")

    app = FastAPI(
        title=configs.PROJECT_NAME,
        lifespan=lifespan,
        description=configs.PROJECT_DESCRIPTION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
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
