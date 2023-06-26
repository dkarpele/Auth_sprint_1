import pytest_asyncio
from sqlalchemy.future import select

from tests.functional.settings import settings
from src.models.entity import User


@pytest_asyncio.fixture(scope='function')
async def select_row(pg_client):
    async def inner(_id: str):
        user = await pg_client.execute(
            select(User).
            filter(User.id == _id)
        )
        await pg_client.commit()
        return user.scalars().all()
    yield inner


@pytest_asyncio.fixture(scope='function')
async def get_access_token(session_client):
    async def inner(payload: dict):
        prefix = '/api/v1/auth'
        postfix = '/login'

        url = settings.service_url + prefix + postfix

        async with session_client.post(url, data=payload) as response:
            body = await response.json()
            return body['access_token']
    yield inner
