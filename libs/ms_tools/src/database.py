from abc import ABC, abstractmethod
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


class DatabaseAdapter(ABC):
    @abstractmethod
    async def get_async_session(self) -> AsyncGenerator[AsyncSession]:
        pass


class SQLAlchemyAdapter(DatabaseAdapter):
    def __init__(self, db_url: str):
        self._engine = create_async_engine(db_url, echo=True)
        self._async_session_maker = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_async_session(self) -> AsyncGenerator[AsyncSession]:
        async with self._async_session_maker() as session:
            yield session
