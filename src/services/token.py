import logging
from datetime import datetime, timedelta
from logging import config as logging_config

from core.logger import LOGGING

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel


from core.config import settings

logging_config.dictConfig(LOGGING)

SECRET_KEY = settings.SECRET_KEY
SECRET_KEY_REFRESH = settings.SECRET_KEY_REFRESH
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 7 days


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(data: dict,
                 expires_delta: timedelta | None = None,
                 _type: str = 'access'):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    if _type == 'access':
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    else:
        # Configure refresh-token
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY_REFRESH,
                                 algorithm=ALGORITHM)
    return encoded_jwt


async def add_not_valid_access_token_to_cache(token, cache):
    """
    Добавляет access-token в cache в виде
    'invalid-access-token:<access-token>' : '<username>'
    :param token:
    :param cache: подключение к DB
    :return:
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    token_expire = payload.get("exp")
    username = payload.get("sub")
    cache_expire = token_expire - int(datetime.timestamp(datetime.now()))
    await cache.put_to_cache_by_id(_id=f'invalid-access-token:{token}',
                                   entity=username,
                                   expire=cache_expire)


async def check_access_token_not_valid(token, cache):
    """
    Проверяет есть ли недействительный access-token в cache
    :param token:
    :param cache: подключение к DB
    :return:
    """
    not_valid = await \
        cache.get_from_cache_by_id(_id=f'invalid-access-token:{token}')
    if not_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        logging.info('Access token is valid')
