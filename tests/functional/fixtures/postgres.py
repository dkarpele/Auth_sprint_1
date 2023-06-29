import pytest_asyncio

from sqlalchemy import delete, insert

from src.models.entity import User
from src.models.roles import Role, UserRole
from src.models.history import LoginHistory
from tests.functional.testdata.pg_data import users, roles, users_roles


@pytest_asyncio.fixture(scope='class')
async def pg_write_data(pg_client):
    data_list = [
        (User, users),
        (Role, roles),
        (UserRole, users_roles),
        (LoginHistory, )]
    for i in data_list:
        await pg_client.execute(delete(i[0]))
        await pg_client.commit()
        try:
            await pg_client.execute(
                    insert(i[0]),
                    i[1],
            )
            await pg_client.commit()
        except IndexError:
            pass

    yield

    for i in data_list:
        await pg_client.execute(delete(i[0]))
        await pg_client.commit()
