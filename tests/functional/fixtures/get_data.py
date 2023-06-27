import pytest_asyncio
from sqlalchemy.future import select

from tests.functional.settings import settings
from src.models.entity import User


@pytest_asyncio.fixture(scope='function')
async def select_row(pg_client):
    async def inner(_id: str, model=User, column=User.id):
        user = await pg_client.execute(
            select(model).
            where(column == _id)
        )
        await pg_client.commit()
        return user.scalars().all()
    yield inner


@pytest_asyncio.fixture(scope='function')
async def get_token(session_client):
    async def inner(payload: dict, token_type: str = 'access'):
        prefix = '/api/v1/auth'
        postfix = '/login'

        url = settings.service_url + prefix + postfix

        async with session_client.post(url, data=payload) as response:
            body = await response.json()
            if token_type == 'access':
                return body['access_token']
            if token_type == 'refresh':
                return body['refresh_token']

    yield inner
