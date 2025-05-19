import asyncio
from core.database import async_session, get_async_session
from repositories.users_repository import UserRepository
from schemas.users import UserRegister


async def create_test_user():
    async for session in get_async_session():
        repo = UserRepository(session)
        test_user = UserRegister(
            email="test@example.com",
            phone_number="89249194507",
            first_name="string",
            last_name="string",
            password="string"
        )
        result = await repo.add_user(test_user)
        if result:
            print("✅Тестовый пользователь создан")
        else:
            print("❌ Пользователь уже существует")



