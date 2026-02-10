from sqlalchemy import select
from core.database import get_async_session
from repositories.levels_repository import LevelsRepository
from models.trainings import Levels

INITIAL_LEVELS = [
    {"value": 1, "label": "Начальный"},
    {"value": 2, "label": "Базовый"},
    {"value": 3, "label": "Средний"},
    {"value": 4, "label": "Повышенный"},
    {"value": 5, "label": "Продвинутый"},
    {"value": 6, "label": "Экспертный"},
    {"value": 7, "label": "Мастерский"},
    {"value": 8, "label": "Профессиональный"},
    {"value": 9, "label": "Специалист"},
]


async def create_initial_levels():
    """
    Создаёт начальные уровни в базе данных, если их нет.
    """
    async for session in get_async_session():
        repo = LevelsRepository(session)
        count = await repo.count()

        if count == 0:
            try:
                for action_data in INITIAL_LEVELS:
                    action = Levels(**action_data)
                    session.add(action)
                await session.commit()
                print(f"Успешно создано {len(INITIAL_LEVELS)} уровней")
            except Exception as e:
                await session.rollback()
                print(f"❌ Ошибка при создании уровней: {e}")
        else:
            print(f"Уровни уже существуют. Всего: {count}")
