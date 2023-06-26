from typing import Annotated

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.future import select

from models.entity import User
from schemas.entity import UserResponseData, UserLogin
from services.token import check_access_token, get_password_hash, Token
from services.users import get_current_active_user
from services.database import get_db_service

router = APIRouter()


@router.get("/me",
            description="Вся информация о пользователе",
            response_model=UserResponseData,
            status_code=HTTPStatus.OK,)
async def read_users_me(
        check_token: Annotated[Token, Depends(check_access_token)],
        current_user: Annotated[User, Depends(get_current_active_user)],
        ) -> UserResponseData:

    return current_user


@router.patch("/change-login-password",
              description="Изменить логин/пароль авторизованного пользователя",
              response_model=UserResponseData,
              status_code=HTTPStatus.OK)
async def change_login_password(
        new_login: UserLogin,
        check_token: Annotated[Token, Depends(check_access_token)],
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: AsyncSession = Depends(get_db_service)) -> UserResponseData:

    async with db:
        user_exists = await db.execute(
            select(User).
            filter(User.email == new_login.email)
        )

        if user_exists.scalars().all():
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=f"Email {new_login.email} already exists",
                headers={"WWW-Authenticate": "Bearer"},
            )
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
