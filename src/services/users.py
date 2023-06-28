import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from services.token import verify_password, TokenData, \
    SECRET_KEY, decode_token, oauth2_scheme
from services.exceptions import credentials_exception
from db.postgres import get_session
from models.entity import User
from models.roles import UserRole, Role
from models.history import LoginHistory
from schemas.entity import UserInDB


async def get_user(_id: str = None,
                   email: str = None,
                   db: AsyncSession = Depends(get_session)):
    async with db:
        if _id:
            user_exists = await db.execute(
                select(User).
                where(User.id == _id))
        elif email:
            user_exists = await db.execute(
                select(User).
                where(User.email == email))
        else:
            raise logging.exception("Parameters _id or email weren't fulfilled")
        user = user_exists.scalars().all()
        if user:
            return UserInDB(**jsonable_encoder(user[0]))


async def authenticate_user(username: str,
                            password: str,
                            db: AsyncSession = Depends(get_session)):
    user = await get_user(email=username, db=db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: AsyncSession = Depends(get_session)):
    _id, _ = await decode_token(token, SECRET_KEY)
    token_data = TokenData(id=_id)
    user = await get_user(_id=token_data.id, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Inactive user",
                            headers={"WWW-Authenticate": "Bearer"})
    return current_user


async def check_admin_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: AsyncSession = Depends(get_session)):
    try:
        user_id, _ = await decode_token(token, SECRET_KEY)

        roles_exists = await db.execute(
            select(UserRole).
            filter(UserRole.user_id == user_id)
        )
        all_roles = [row.role_id for row in roles_exists.scalars().all()]
        permissions = 0
        for r_id in all_roles:
            response = await db.execute(select(Role).filter(Role.id == r_id))
            role = response.scalars().first()
            if role.permissions > permissions:
                permissions = role.permissions
        admin = await db.execute(
            select(Role).
            filter(Role.title == 'admin')
        )
        if admin.scalars().first().permissions <= permissions:
            return True
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to access on "
                                   "this server.",
                            headers={"WWW-Authenticate": "Bearer"})
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Role admin not found.",
                            headers={"WWW-Authenticate": "Bearer"})


async def add_history(user_id: UUID,
                      source: str = None,
                      db: AsyncSession = Depends(get_session)) -> None:
    history = LoginHistory(user_id, source)
    db.add(history)
    await db.commit()
    await db.refresh(history)
