from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from api.v1 import check_entity_exists
from models.entity import User
from models.roles import UserRole, Role
from schemas.entity import UserResponseData, UserLogin, UserRoleInDB, UserRoleCreate
from schemas.roles import RoleCreate
from services.token import check_access_token, get_password_hash, Token
from services.users import get_current_active_user, check_admin_user
from services.database import get_db_service


router = APIRouter()


@router.get("/me",
            description="Вся информация о пользователе",
            response_model=UserResponseData,
            status_code=status.HTTP_200_OK)
async def read_users_me(
        check_token: Annotated[Token, Depends(check_access_token)],
        current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponseData:
    return current_user


@router.patch("/change-login-password",
              description="Изменить логин/пароль авторизованного пользователя",
              response_model=UserResponseData,
              status_code=status.HTTP_200_OK)
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
                status_code=status.HTTP_401_UNAUTHORIZED,
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


@router.post("/add-role",
             description="Добавить роль для пользователя",
             response_model=UserRoleInDB,
             status_code=status.HTTP_201_CREATED)
async def add_role(
        user_role: UserRoleCreate,
        check_token: Annotated[Token, Depends(check_access_token)],
        current_user: Annotated[User, Depends(get_current_active_user)],
        check_admin: Annotated[bool, Depends(check_admin_user)],
        db: AsyncSession = Depends(get_db_service)) -> UserRoleInDB:
    try:

        async with db:
            await check_entity_exists(db, User, user_role.user_id)
            await check_entity_exists(db, Role, user_role.role_id)

            roles_exists = await db.execute(
                select(UserRole).
                filter(UserRole.user_id == user_role.user_id)
            )
            all_roles = [row.role_id for row in roles_exists.scalars().all()]
            if user_role.role_id in all_roles:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Role {user_role.role_id} already exists for user "
                           f"{user_role.user_id}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user_role_db = UserRole(user_role.user_id, user_role.role_id)
            db.add(user_role_db)
            await db.commit()
            await db.refresh(user_role_db)
            return UserRoleInDB(id=user_role_db.id,
                                user_id=user_role_db.user_id,
                                role_id=user_role_db.role_id)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"role_id: {user_role_db.role_id} OR "
                                   f"user_id: {user_role_db.user_id} not "
                                   f"found",
                            headers={"WWW-Authenticate": "Bearer"})


@router.delete("/delete-role",
               description="Удалить роль у пользователя",
               response_model=None,
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
        user_role: UserRoleCreate,
        check_token: Annotated[Token, Depends(check_access_token)],
        current_user: Annotated[User, Depends(get_current_active_user)],
        check_admin: Annotated[bool, Depends(check_admin_user)],
        db: AsyncSession = Depends(get_db_service)) -> None:
    async with db:
        await check_entity_exists(db, User, user_role.user_id)
        await check_entity_exists(db, Role, user_role.role_id)

        roles_exists = await db.execute(
            select(UserRole).
            filter(UserRole.user_id == user_role.user_id)
        )
        all_rows = roles_exists.scalars().all()
        if user_role.role_id not in [row.role_id for row in all_rows]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID: {user_role.role_id} not found for user"
                       f" {user_role.user_id}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_role_db = [row for row in all_rows
                        if user_role.role_id == row.role_id][0]
        await db.delete(user_role_db)
        await db.commit()


@router.get('/roles',
            response_model=list[RoleCreate],
            status_code=status.HTTP_200_OK,
            description="просмотр всех ролей пользователя")
async def get_all_roles(
        user_id: str,
        check_token: Annotated[Token, Depends(check_access_token)],
        check_admin: Annotated[bool, Depends(check_admin_user)],
        db: AsyncSession = Depends(get_db_service)) -> list[RoleCreate]:
    async with db:
        await check_entity_exists(db, User, user_id)

        roles_exists = await db.execute(
            select(UserRole).
            filter(UserRole.user_id == user_id)
        )
        all_roles = [row.role_id for row in roles_exists.scalars().all()]
        roles = []
        for r_id in all_roles:
            response = await db.execute(
                select(Role).
                filter(Role.id == r_id)
            )
            role = response.scalars().all()[0]
            roles.append(RoleCreate(title=role.title,
                                    permissions=role.permissions))
        return roles
