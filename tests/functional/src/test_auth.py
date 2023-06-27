import logging
from asyncio import sleep

import aiohttp
import pytest

from http import HTTPStatus
from logging import config as logging_config

from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
pytestmark = pytest.mark.asyncio

PREFIX = '/api/v1/auth'


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestSignup:
    postfix = '/signup'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {"first_name": "string",
                     "last_name": "string",
                     "disabled": False,
                     "email": "test@example.com",
                     "password": "Secret123"
                     },
                    {'status': HTTPStatus.CREATED},
            ),
        ]
    )
    async def test_create_user(self,
                               session_client,
                               select_row,
                               payload,
                               expected_answer):
        url = settings.service_url + PREFIX + self.postfix

        async with session_client.post(url, json=payload) as response:
            body = await response.json()
            user = await select_row(body['id'])

            assert response.status == expected_answer['status']
            assert 'password' not in body.keys()
            assert 'id' in body.keys()

            assert str(user[0].id) == body['id']
            assert user[0].password != payload['password']

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {"first_name": "string",
                     "last_name": "string",
                     "disabled": False,
                     "email": "user-0@example.com",
                     "password": "Secret123"
                     },
                    {'status': HTTPStatus.UNAUTHORIZED,
                     'detail': 'Email user-0@example.com already exists'},
            ),
        ]
    )
    async def test_create_user_exists(self,
                                      session_client,
                                      payload,
                                      expected_answer):
        url = settings.service_url + PREFIX + self.postfix

        async with session_client.post(url, json=payload) as response:
            body = await response.json()

            assert response.status == expected_answer['status']
            assert body['detail'] == expected_answer['detail']

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                {"first_name": "fn",
                 "last_name": "ln"*50,
                 "disabled": False,
                 "email": "user-0@example",
                 "password": "supersecret"
                 },
                {'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                 'msg_first_name': 'ensure this value has at least 3 '
                                   'characters',
                 'msg_last_name': 'ensure this value has at most 50 '
                                  'characters',
                 'msg_email': 'value is not a valid email address',
                 'msg_password': 'string does not match regex'},
            ),
        ]
    )
    async def test_create_user_negative(self,
                                        session_client,
                                        payload,
                                        expected_answer):
        url = settings.service_url + PREFIX + self.postfix

        async with session_client.post(url, json=payload) as response:
            body = await response.json()
            body = body['detail']
            assert response.status == expected_answer['status']
            assert body[0]['msg'] == expected_answer['msg_first_name']
            assert body[1]['msg'] == expected_answer['msg_last_name']
            assert body[2]['msg'] == expected_answer['msg_email']
            assert expected_answer['msg_password'] in body[3]['msg']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestLogin:
    postfix = '/login'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {"username": "user-0@example.com",
                     "password": "Secret123"
                     },
                    {'status': HTTPStatus.OK},
            ),
        ]
    )
    async def test_login_user(self,
                              session_client,
                              payload,
                              expected_answer):
        url = settings.service_url + PREFIX + self.postfix

        async with session_client.post(url, data=payload) as response:
            body = await response.json()

            assert response.status == expected_answer['status']
            assert 'access_token' in body.keys()
            assert 'access_token_expires' in body.keys()
            assert body['token_type'] == "bearer"

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {"username": "notexists@example.com",
                     "password": "Secret123"
                     },
                    {'status': HTTPStatus.UNAUTHORIZED,
                     'detail': 'Incorrect username or password'},
            ),
            (
                    {"username": "user-0@example.com",
                     "password": "bad_password"
                     },
                    {'status': HTTPStatus.UNAUTHORIZED,
                     'detail': 'Incorrect username or password'},
            ),
        ]
    )
    async def test_login_user_not_exists(self,
                                         session_client,
                                         payload,
                                         expected_answer):
        url = settings.service_url + PREFIX + self.postfix

        async with session_client.post(url, data=payload) as response:
            body = await response.json()

            assert response.status == expected_answer['status']
            assert body['detail'] == expected_answer['detail']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestLogout:
    postfix = '/logout'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {"username": "user-0@example.com",
                     "password": "Secret123"},
                    {'status': HTTPStatus.OK}
             ),
        ]
    )
    async def test_logout_user(self,
                               get_token,
                               payload,
                               expected_answer):
        url = settings.service_url + PREFIX + self.postfix
        global access_token
        access_token = await get_token(payload)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.post(url) as response:
                assert response.status == expected_answer['status']

    async def test_logout_user_the_same_token(self):
        url = settings.service_url + PREFIX + self.postfix
        try:
            header = {'Authorization': f'Bearer {access_token}'}
        except NameError:
            logging.error(f"Can't run the test with unknown access_token")
            assert False

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.post(url) as response:
                assert response.status == HTTPStatus.UNAUTHORIZED

    @pytest.mark.parametrize(
        'expected_answer',
        [
            {'status': HTTPStatus.UNAUTHORIZED,
             'detail': 'Not authenticated'},
        ]
    )
    async def test_logout_user_unauth(self,
                                      session_client,
                                      expected_answer):
        url = settings.service_url + PREFIX + self.postfix

        async with session_client.post(url) as response:
            body = await response.json()

            assert response.status == expected_answer['status']
            assert body['detail'] == expected_answer['detail']


@pytest.mark.usefixtures('redis_clear_data_before_after',
                         'pg_write_data')
class TestRefresh:
    postfix = '/refresh'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {"username": "user-0@example.com",
                     "password": "Secret123"},
                    {'status': HTTPStatus.OK}
             ),
        ]
    )
    async def test_refresh_tokens(self,
                                  session_client,
                                  get_token,
                                  payload,
                                  expected_answer):

        refresh_token = await get_token(payload, 'refresh')
        url = settings.service_url + PREFIX + self.postfix \
                                            + f'?token={refresh_token}'
        # Without sleep tokens will be created at exactly the same time and
        # will be equal.
        await sleep(1)
        async with session_client.post(url) as response:
            body = await response.json()

            assert response.status == expected_answer['status']
            assert body['refresh_token'] != refresh_token
            assert 'access_token' in body.keys()
            assert 'access_token_expires' in body.keys()
