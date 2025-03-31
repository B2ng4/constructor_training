from fastapi import FastAPI

import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from starlette.responses import HTMLResponse


def create_base_app(configs):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
        """Управление жизненным циклом приложения."""
        logger.info("Инициализация приложения...")
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
