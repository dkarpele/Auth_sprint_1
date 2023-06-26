import aiohttp
import asyncio
import redis
import pytest_asyncio
from sqlalchemy.future import select

from tests.functional.settings import settings, database_dsn
from src.db import postgres
from src.models.entity import User

pytest_plugins = ("tests.functional.fixtures.get_data",
                  "tests.functional.fixtures.redis",
                  "tests.functional.fixtures.postgres",)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def pg_client():
    postgres.postgres = postgres.Postgres(
                      f'postgresql+asyncpg://'
                      f'{database_dsn.user}:{database_dsn.password}@'
                      f'{database_dsn.host}:{database_dsn.port}/'
                      f'{database_dsn.dbname}')

    async with postgres.postgres.async_session() as session:
        await postgres.postgres.create_database()
        yield session
        await postgres.postgres.purge_database()
        await postgres.postgres.close()


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    client = redis.Redis(host=settings.redis_host,
                         port=settings.redis_port)
    yield client
    client.close()


@pytest_asyncio.fixture(scope='session')
async def session_client():
    client = aiohttp.ClientSession()
    yield client
    await client.close()
