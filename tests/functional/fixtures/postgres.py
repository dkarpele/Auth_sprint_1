import pytest_asyncio

from sqlalchemy import delete, insert
from sqlalchemy.future import select


from src.models.entity import User
from src.models.roles import Role
from tests.functional.testdata.pg_data import users, roles
from tests.functional.settings import settings, database_dsn


@pytest_asyncio.fixture(scope='class')
async def pg_write_data(pg_client):
    await pg_client.execute(
            insert(User),
            users,
    )
    await pg_client.commit()
    await pg_client.execute(
            insert(Role),
            roles,
    )
    await pg_client.commit()

    yield

    await pg_client.execute(delete(User))
    await pg_client.commit()
    await pg_client.execute(delete(Role))
    await pg_client.commit()



