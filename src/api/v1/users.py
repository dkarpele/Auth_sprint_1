from typing import Annotated

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.future import select

from api.helpers.token import get_password_hash
from db.postgres import get_session
from models.entity import User
from schemas.entity import UserResponseData, UserLogin, UserEmail
from api.helpers.users import get_current_active_user
# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get("/me",
            description="Вся информация о пользователе",
            response_model=UserResponseData,
            status_code=HTTPStatus.OK,)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]) \
        -> UserResponseData:
    return current_user


@router.patch("/change-login-password",
              description="Изменить логин/пароль авторизованного пользователя",
              response_model=UserResponseData,
              status_code=HTTPStatus.OK)
async def change_login_password(
        new_login: UserLogin,
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: AsyncSession = Depends(get_session)) -> UserResponseData:

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
