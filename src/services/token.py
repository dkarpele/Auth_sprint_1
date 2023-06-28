import logging
from datetime import datetime, timedelta
from logging import config as logging_config
from typing import Annotated

from core.logger import LOGGING

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel


from core.config import settings
from db import AbstractCache
from services.database import get_cache_service
from services.exceptions import credentials_exception, \
    access_token_invalid_exception, relogin_exception

logging_config.dictConfig(LOGGING)

SECRET_KEY = settings.secret_key
SECRET_KEY_REFRESH = settings.secret_key_refresh
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 7 days


class Token(BaseModel):
    access_token: str
    access_token_expires: datetime | int
    refresh_token: str = None
    refresh_token_expires: datetime | int = None
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_token(
        data: dict,
        cache: AbstractCache = Depends(get_cache_service)) -> dict:
    access_token_expires =\
        datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = \
        datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()

    # Configure access-token
    to_encode.update({"exp": access_token_expires})
    access_token = jwt.encode(to_encode,
                              SECRET_KEY,
                              algorithm=ALGORITHM)

    # Configure refresh-token
    to_encode.update({"exp": refresh_token_expires})
    refresh_token = jwt.encode(to_encode,
                               SECRET_KEY_REFRESH,
                               algorithm=ALGORITHM)

    # Put to cache `{refresh_token}:{user_id}` to receive user id from refresh
    # token. It will be used later to create access token from user id. Will be
    # kept in cache for REFRESH_TOKEN_EXPIRE_MINUTES in seconds.
    await cache.put_to_cache_by_id(_id=refresh_token,
                                   entity=to_encode['sub'],
                                   expire=int(REFRESH_TOKEN_EXPIRE_MINUTES*60))

    return {'access_token': access_token,
            'refresh_token': refresh_token,
            'access_token_expires': access_token_expires,
            'refresh_token_expires': refresh_token_expires,
            "token_type": "bearer"}


async def decode_token(token: str, key: str) -> tuple[str, str]:
    try:
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        token_expire = payload.get("exp")
        sub = payload.get("sub")
        cache_expire = token_expire - int(datetime.timestamp(datetime.now()))
        if sub is None:
            raise credentials_exception
        return sub, cache_expire
    except JWTError:
        raise credentials_exception


async def check_access_token(
        token: Annotated[str, Depends(oauth2_scheme)],
        cache: AbstractCache = Depends(get_cache_service),):
    """
    Проверяет есть ли недействительный access-token в cache
    :param token:
    :param cache: подключение к DB
    :return:
    """
    # Check if access token isn't valid (User logged out)
    not_valid = await \
        cache.get_from_cache_by_id(_id=f'invalid-access-token:{token}')
    if not_valid or token == 'undefined':
        raise credentials_exception

    try:
        # Check if access token is expired. If yes - ask to create new pair
        # using /refresh method
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logging.info('Access token is valid')
        return Token(**{"access_token": token,
                        "token_type": "bearer",
                        "access_token_expires": payload.get("exp")})
    except ExpiredSignatureError:
        raise access_token_invalid_exception


async def refresh_access_token(
        refresh_token: str,
        cache: AbstractCache):
    """
    Обновляет access token по refresh token
    :param refresh_token: refresh token
    :param cache: подключение к DB
    :return:
    """
    # If refresh token is invalid - exit immediately
    try:
        jwt.decode(refresh_token, SECRET_KEY_REFRESH, algorithms=[ALGORITHM])
    except JWTError:
        raise relogin_exception

    # check id from refresh token exists in cache
    user_id = await cache.get_from_cache_by_id(_id=refresh_token)

    # If it doesn't exist then refresh token was expired or user never logged
    # in or refresh token has already been used
    if not user_id:
        raise relogin_exception

    # remove refresh-token:user_id from cache, we will create new pair
    await cache.delete_from_cache_by_id(_id=refresh_token)

    # create a new pair of tokens using id
    token_structure = await create_token({"sub": str(user_id, 'utf-8')}, cache)

    return Token(**token_structure)


async def add_not_valid_access_token_to_cache(
        token: Token,
        cache: AbstractCache) -> None:
    """
    Добавляет access-token в cache в виде
    'invalid-access-token:<access-token>' : '<username>'
    :param token:
    :param cache: подключение к DB
    :return:
    """
    sub, cache_expire = await decode_token(token.access_token, SECRET_KEY)
    await cache.put_to_cache_by_id(
                            _id=f'invalid-access-token:{token.access_token}',
                            entity=sub,
                            expire=cache_expire)
