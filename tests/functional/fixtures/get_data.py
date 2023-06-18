import pytest_asyncio

from tests.functional.settings import settings


@pytest_asyncio.fixture(scope='function')
async def get_id(session_client):
    async def inner(prefix: str):
        url = settings.service_url + prefix

        async with session_client.get(url) as response:
            body = await response.json()
            return body[0]['uuid']
    yield inner
