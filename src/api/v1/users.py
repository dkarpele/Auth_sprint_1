from typing import Annotated

from http import HTTPStatus
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.future import select

from db import AbstractCache
from db.postgres import get_session
from db.redis import Redis, get_redis
from models.entity import User
from schemas.entity import UserResponseData, UserLogin
from services.token import check_access_token_not_valid, get_password_hash,\
    oauth2_scheme
from services.users import get_current_active_user
from services.database import get_db_service, get_cache_service

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get("/me",
            description="Вся информация о пользователе",
            response_model=UserResponseData,
            status_code=HTTPStatus.OK,)
async def read_users_me(
        token: Annotated[str, Depends(oauth2_scheme)],
        current_user: Annotated[User, Depends(get_current_active_user)],
        cache: AbstractCache = Depends(get_cache_service),
) -> UserResponseData:

    await check_access_token_not_valid(token, cache)
    return current_user


@router.patch("/change-login-password",
              description="Изменить логин/пароль авторизованного пользователя",
              response_model=UserResponseData,
              status_code=HTTPStatus.OK)
async def change_login_password(
        new_login: UserLogin,
        token: Annotated[str, Depends(oauth2_scheme)],
        current_user: Annotated[User, Depends(get_current_active_user)],
        cache: AbstractCache = Depends(get_cache_service),
        db: AsyncSession = Depends(get_db_service)) -> UserResponseData:

    await check_access_token_not_valid(token, cache)
    async with db:
        await db.execute(update(User).
                         where(User.email == current_user.email).
                         values(password=get_password_hash(new_login.password),
                                email=new_login.email))
        await db.commit()
        new_user = await db.execute(
            select(User).
            filter(User.email == new_login.email))
        new_user = new_user.scalars().all()
        if new_user:
            return UserResponseData(**jsonable_encoder(new_user[0]))
