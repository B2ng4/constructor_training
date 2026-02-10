from sqlalchemy import select
from core.database import get_async_session
from repositories.actions_repository import ActionsRepository
from models.trainings import TypesAction

INITIAL_ACTIONS = [
    {"id": 1, "type": "leftClick", "name": "Левый клик", "meta": {"icon": "LeftClick"}},
    {"id": 2, "type": "rightClick", "name": "Правый клик", "meta": {"icon": "RightClick"}},
    {"id": 3, "type": "doubleClick", "name": "Двойной клик", "meta": {"icon": "DoubleClick"}},
    {"id": 4, "type": "hover", "name": "Наведение курсора", "meta": {"icon": "Hover"}},
    {"id": 5, "type": "inputText", "name": "Ввод текста", "meta": {"icon": "Input"}},
    {"id": 6, "type": "keyPress", "name": "Нажатие клавиши", "meta": {"icon": "Keyboard"}},
]


async def create_initial_actions():
    """
    Создаёт начальные типы действий, если таблица пуста.
    """
    async for session in get_async_session():
        repo = ActionsRepository(session)
        count = await repo.count()

        if count == 0:
            try:
                for action_data in INITIAL_ACTIONS:
                    action = TypesAction(**action_data)
                    session.add(action)
                await session.commit()
                print(f"Успешно создано {len(INITIAL_ACTIONS)} типов действий")
            except Exception as e:
                await session.rollback()
                print(f"❌ Ошибка при создании действий: {e}")
        else:
            print(f"Типы действий уже существуют. Всего: {count}")
