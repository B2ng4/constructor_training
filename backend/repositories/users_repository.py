from sqlalchemy import func

from models.users import User
from schemas.users import UserRegister
from utils.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.future import select


class UserRepository:
    """Репозиторий пользователей"""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_one_or_none(self, email: str) -> User:
        """Поиск пользователя по email"""
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def add_user(self, user: UserRegister) -> bool:
        """Добавление пользователя"""
        existing_user = await self.find_one_or_none(user.email)
        if existing_user:
            return False
        db_user = User(
            email=user.email,
            password=get_password_hash(user.password),
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        self.session.add(db_user)
        await self.session.commit()
        return True



    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return await self.session.get(User, user_id)



    async def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True



    async def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Обновление данных пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for key, value in user_data.items():
            if hasattr(user, key) and key != "password":
                setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user



    async def change_password(self, user_id: int, new_password: str) -> bool:
        """Изменение пароля пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        user.password = get_password_hash(new_password)
        await self.session.commit()
        return True


    async def count_users(self) -> int:
        """Количество всех пользователей"""
        query = select(func.count()).select_from(User)
        result = await self.session.execute(query)
        return result.scalar()


