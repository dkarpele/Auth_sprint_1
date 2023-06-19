from db import AbstractStorage
from sqlalchemy.orm import declarative_base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, \
    async_sessionmaker

# Создаём базовый класс для будущих моделей
Base = declarative_base()


class Postgres(AbstractStorage):
    def __init__(self, url: str):
        self.engine = create_async_engine(url,
                                          echo=True,
                                          future=True)

        self.async_session = async_sessionmaker(self.engine,
                                                class_=AsyncSession,
                                                expire_on_commit=False)

    async def close(self):
        ...

    async def create_database(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def purge_database(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


postgres: Postgres | None = None


# Функция понадобится при внедрении зависимостей
# Dependency
async def get_session() -> AsyncSession:
    async with postgres.async_session() as session:
        yield session
