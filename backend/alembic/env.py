import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool, engine_from_config
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from core.database import Base, DATABASE_URL

from models.users import *
from models.events import *


# this is the Alembic Config object
config = context.config

# заменяем URL базы данных на ваш асинхронный URL
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Интерпретируем файл конфигурации, если он присутствует
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Добавляем модель MetaData для автогенерации миграций
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в 'офлайн' режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Запуск миграций в 'онлайн' режиме."""
    # Создаем асинхронный движок вручную
    connectable = create_async_engine(DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

def run_async_migrations() -> None:
    """Запуск асинхронных миграций."""
    asyncio.run(run_migrations_online())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_async_migrations()