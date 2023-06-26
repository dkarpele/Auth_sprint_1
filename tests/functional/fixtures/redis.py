import pytest_asyncio


@pytest_asyncio.fixture(scope='class')
async def redis_clear_data_before_after(redis_client):
    redis_client.flushall()
    yield
    redis_client.flushall()


@pytest_asyncio.fixture(scope='class')
async def redis_clear_data_after(redis_client):
    yield
    redis_client.flushall()


@pytest_asyncio.fixture(scope='class')
async def redis_clear_data_before(redis_client):
    redis_client.flushall()
    yield


