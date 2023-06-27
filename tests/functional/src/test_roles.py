import aiohttp
import pytest

from http import HTTPStatus
from logging import config as logging_config

from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

from src.models.roles import Role

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
pytestmark = pytest.mark.asyncio

PREFIX = '/api/v1/roles'


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestCreate:
    postfix = '/create'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {"title": "manager",
                     "permissions": 4},
                    {'status': HTTPStatus.CREATED},
            ),
        ]
    )
    async def test_create_role(self,
                               get_token,
                               select_row,
                               payload,
                               expected_answer):
        url = settings.service_url + PREFIX + self.postfix
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.post(url, json=payload) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                role = await select_row(body['id'], Role, Role.id)

                assert 'id' in body.keys()

                assert str(role[0].id) == body['id']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestGet:
    postfix = '/'

    @pytest.mark.parametrize(
        'expected_answer',
        [
            {'status': HTTPStatus.OK,
             'titles': ['admin', 'content-manager', 'subscriber', 'viewer']}
        ]
    )
    async def test_get_roles(self,
                             get_token,
                             expected_answer):
        url = settings.service_url + PREFIX + self.postfix
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(url) as response:
                assert response.status == expected_answer['status']

                body = await response.json()

                titles = [row['title'] for row in body]
                assert titles == expected_answer['titles']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestUpdateRole:
    postfix = '/'

    @pytest.mark.parametrize(
        'param, payload, expected_answer',
        [
            (
                    '0a1af085-c8c4-49c0-8407-6f032589e614',
                    {"title": "manager",
                     "permissions": 4},
                    {'status': HTTPStatus.OK,
                     'title': 'manager'}
             )

        ]
    )
    async def test_update_role(self,
                               get_token,
                               select_row,
                               param,
                               payload,
                               expected_answer):
        url = settings.service_url + PREFIX + self.postfix + f'{param}'
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.patch(url, json=payload) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                role = await select_row(body['id'], Role, Role.id)

                assert str(role[0].title) == expected_answer['title']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestDeleteRole:
    postfix = '/delete'

    @pytest.mark.parametrize(
        'param, expected_answer',
        [
            (
                    '0a1af085-c8c4-49c0-8407-6f032589e614',
                    {'status': HTTPStatus.NO_CONTENT}
             )

        ]
    )
    async def test_update_role(self,
                               get_token,
                               select_row,
                               param,
                               expected_answer):
        url = settings.service_url + PREFIX + self.postfix + f'/{param}'
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.delete(url) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                role = await select_row(param, Role, Role.id)

                assert not body
                assert not role
