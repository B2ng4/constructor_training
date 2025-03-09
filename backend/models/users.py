from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column
from core.database import *
import asyncio


Base.metadata.clear()


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column()
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"




async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)




if __name__ == "__main__":
    asyncio.run(create_tables())
else:
    try:
        asyncio.run(create_tables())
    except RuntimeError as e:
        print(f"Could not create tables on import: {e}")