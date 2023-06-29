from datetime import datetime

import aiohttp
import pytest

from http import HTTPStatus
from logging import config as logging_config

from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

from src.models.roles import UserRole

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
pytestmark = pytest.mark.asyncio

PREFIX = '/api/v1/users'


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestGet:
    postfix = '/me'

    @pytest.mark.parametrize(
        'access_data, expected_answer',
        [
            (
              {"username": "admin@example.com",
               "password": "Secret123"},
              {'status': HTTPStatus.OK,
               "id": "e9756a00-73d6-455c-8bfa-734d859867b0",
               "first_name": "Admin",
               "last_name": "Admin",
               "disabled": False,
               "email": "admin@example.com",
               }
            )
        ]
    )
    async def test_get_user(self,
                            get_token,
                            access_data,
                            expected_answer):
        url = settings.service_url + PREFIX + self.postfix

        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(url) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                assert body['first_name'] == expected_answer['first_name']
                assert body['email'] == expected_answer['email']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestChangeLoginPassword:
    postfix = '/change-login-password'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {"email": "new-user@example.com",
                     "password": "fCBV6J6W38Q6f0DJfu50d5CIPHSAO8V81f5Y"},
                    {'status': HTTPStatus.OK,
                     "first_name": 'Name-0',
                     "last_name": 'Surname-0',
                     "disabled": False,
                     "email": 'new-user@example.com',
                     }
             )

        ]
    )
    async def test_update_role(self,
                               get_token,
                               select_row,
                               payload,
                               expected_answer):
        url = settings.service_url + PREFIX + self.postfix
        access_data = {"username": "user-0@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.patch(url, json=payload) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                role = await select_row(body['id'])

                assert str(role[0].email) == expected_answer['email']
                assert str(role[0].first_name) == expected_answer['first_name']
                assert str(role[0].password) != payload['password']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestAddRole:
    postfix = '/add-role'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "user_id": "e9756a00-73d6-455c-8bfa-734d859867b0",
                        "role_id": "0a1af085-c8c4-49c0-8407-6f032589e614"
                    },
                    {'status': HTTPStatus.CREATED,
                     "role_id": "0a1af085-c8c4-49c0-8407-6f032589e614"},
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
                role = await select_row(body['user_id'],
                                        UserRole,
                                        UserRole.user_id)

                assert str(role[1].role_id) == expected_answer['role_id']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestDeleteRole:
    postfix = '/delete-role'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "user_id": "e9756a00-73d6-455c-8bfa-734d859867b0",
                        "role_id": "c1c3c6fc-95df-49cd-81f1-873f0128c404"
                    },
                    {'status': HTTPStatus.NO_CONTENT},
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
            async with session.delete(url, json=payload) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                role = await select_row(payload['user_id'],
                                        UserRole,
                                        UserRole.user_id)

                assert not body
                assert not role


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestGetRoles:
    postfix = '/roles'

    @pytest.mark.parametrize(
        'param, expected_answer',
        [
            (
                'e9756a00-73d6-455c-8bfa-734d859867b0',
                {'status': HTTPStatus.OK,
                 'permissions': 7,
                 'title': 'admin'}
            ),
        ]
    )
    async def test_get_roles(self,
                             get_token,
                             param,
                             expected_answer):

        url = settings.service_url + PREFIX + self.postfix \
                                            + f'?user_id={param}'
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(url) as response:
                assert response.status == expected_answer['status']
                body = await response.json()
                assert body[0]['permissions'] == expected_answer['permissions']
                assert body[0]['title'] == expected_answer['title']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestLoginHistory:
    postfix = '/login-history'

    @pytest.mark.parametrize(
        'access_data, expected_answer',
        [
            (
              {"username": "admin@example.com",
               "password": "Secret123"},
              {'status': HTTPStatus.OK,
               "user_id": "e9756a00-73d6-455c-8bfa-734d859867b0",
               "login_time_format": "%Y-%m-%dT%H:%M:%S",
               }
            )
        ]
    )
    async def test_get_user(self,
                            get_token,
                            access_data,
                            expected_answer):
        url = settings.service_url + PREFIX + self.postfix

        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(url) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                assert body[0]['user_id'] == expected_answer['user_id']
                assert datetime.strptime(
                    body[0]['login_time'][:body[0]['login_time'].rfind('.')],
                    expected_answer['login_time_format'])
