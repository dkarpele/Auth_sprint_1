from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from api.v1 import check_entity_exists
from models.model import PaginateModel
from services.users import CurrentUserDep, CheckAdminDep
from services.database import DbDep
from models.users import User
from models.history import LoginHistory
from models.roles import UserRole, Role
from schemas.users import UserResponseData, UserLogin, UserRoleInDB, \
    UserRoleCreate, UserHistory
from schemas.roles import RoleCreate
from services.token import get_password_hash

router = APIRouter()
Paginate = Annotated[PaginateModel, Depends(PaginateModel)]


@router.get("/me",
            description="Вся информация о пользователе",
            response_model=UserResponseData,
            status_code=status.HTTP_200_OK)
async def read_users_me(current_user: CurrentUserDep) -> UserResponseData:
    return current_user


@router.patch("/change-login-password",
              description="Изменить логин/пароль авторизованного пользователя",
              response_model=UserResponseData,
              status_code=status.HTTP_200_OK)
async def change_login_password(
        new_login: UserLogin,
        current_user: CurrentUserDep,
        db: DbDep) -> UserResponseData:
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


@router.get("/login-history",
            description="История логинов пользователя",
            response_model=list[UserHistory],
            status_code=status.HTTP_200_OK)
async def get_login_history(current_user: CurrentUserDep,
                            db: DbDep,
                            pagination: Paginate) -> list[UserHistory]:

    page_number = pagination.page_number
    page_size = pagination.page_size

    history_exists = await db.execute(
        select(LoginHistory).
        filter(LoginHistory.user_id == current_user.id).
        order_by(LoginHistory.login_time.desc()).
        offset((page_number - 1) * page_size).
        limit(page_size)
    )
    history = history_exists.scalars().all()
    return [UserHistory(user_id=h.user_id,
                        source=h.source,
                        login_time=h.login_time) for h in history]


@router.post("/add-role",
             description="Добавить роль для пользователя",
             response_model=UserRoleInDB,
             status_code=status.HTTP_201_CREATED)
async def add_role(user_role: UserRoleCreate,
                   check_admin: CheckAdminDep,
                   db: DbDep) -> UserRoleInDB:
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
async def delete_role(user_role: UserRoleCreate,
                      check_admin: CheckAdminDep,
                      db: DbDep) -> None:
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
async def get_all_roles(user_id: str,
                        check_admin: CheckAdminDep,
                        db: DbDep) -> list[RoleCreate]:
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
            role = response.scalars().first()
            roles.append(RoleCreate(title=role.title,
                                    permissions=role.permissions))
        return roles
