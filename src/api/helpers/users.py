from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.helpers.token import verify_password, TokenData, ALGORITHM, \
    SECRET_KEY, oauth2_scheme
from db.postgres import get_session
from models.entity import User
from schemas.entity import UserInDB


async def get_user(username: str,
                   db: AsyncSession = Depends(get_session)):
    async with db:
        user_exists = await db.execute(
                select(User).
                where(User.email == username))
        user = user_exists.scalars().all()
        if user:
            return UserInDB(**jsonable_encoder(user[0]))


async def authenticate_user(username: str,
                            password: str,
                            db: AsyncSession = Depends(get_session)):
    user = await get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
