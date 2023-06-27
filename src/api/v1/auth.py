from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.exceptions import wrong_username_or_password
from services.token import Token, create_token, \
    add_not_valid_access_token_to_cache, check_access_token, \
    refresh_access_token
from services.users import authenticate_user
from models.entity import User

from db import AbstractCache
from schemas.entity import UserSignUp, UserResponseData
from services.database import get_db_service, get_cache_service

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.post('/signup',
             response_model=UserResponseData,
             status_code=HTTPStatus.CREATED,
             description="регистрация нового пользователя",
             response_description="id, email, hashed password")
async def create_user(
        user_create: UserSignUp,
        db: AsyncSession = Depends(get_db_service)) -> UserResponseData:
    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)
    async with db:
        user_exists = await db.execute(
            select(User).filter(User.email == user.email))

        if user_exists.scalars().all():
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=f"Email {user.email} already exists",
                headers={"WWW-Authenticate": "Bearer"},
            )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


@router.post("/login",
             response_model=Token,
             status_code=HTTPStatus.OK,
             description="login существующего пользователя",
             response_description=""
             )
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_db_service),
        cache: AbstractCache = Depends(get_cache_service)) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise wrong_username_or_password

    token_structure = await create_token({"sub": str(user.id)}, cache)
    return Token(**token_structure)


@router.post("/logout",
             description="выход пользователя из аккаунта",
             status_code=HTTPStatus.OK)
async def logout(
        token: Annotated[Token, Depends(check_access_token)],
        cache: AbstractCache = Depends(get_cache_service),) -> None:
    await add_not_valid_access_token_to_cache(token, cache)


@router.post("/refresh",
             response_model=Token,
             description="получить новую пару access/refresh token",
             status_code=HTTPStatus.OK)
async def refresh(token: str,
                  cache: AbstractCache = Depends(get_cache_service)) -> Token:
    res = await refresh_access_token(token, cache)
    return res
