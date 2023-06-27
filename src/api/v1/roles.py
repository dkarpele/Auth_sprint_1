from typing import Annotated
from fastapi.encoders import jsonable_encoder

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1 import check_entity_exists
from services.database import get_db_service
from services.token import check_access_token, Token
from services.users import check_admin_user

from models.roles import Role
from db.postgres import get_session
from schemas.roles import RoleInDB, RoleCreate

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.post('/create',
             response_model=RoleInDB,
             status_code=HTTPStatus.CREATED,
             description="создание новой роли",
             response_description="id, title, permissions")
async def create_role(
        role_create: RoleCreate,
        check_token: Annotated[Token, Depends(check_access_token)],
        check_admin: Annotated[bool, Depends(check_admin_user)],
        db: AsyncSession = Depends(get_db_service)) -> RoleInDB:
    role_dto = jsonable_encoder(role_create)
    role = Role(**role_dto)
    async with db:
        role_exists = await db.execute(
            select(Role).filter(Role.title == role.title))

        if role_exists.scalars().all():
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=f"Role {role.title} already exists",
                headers={"WWW-Authenticate": "Bearer"}
            )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.get('/',
            response_model=list[RoleInDB],
            status_code=HTTPStatus.OK,
            description="просмотр всех ролей")
async def get_all_roles(
        check_token: Annotated[Token, Depends(check_access_token)],
        check_admin: Annotated[bool, Depends(check_admin_user)],
        db: AsyncSession = Depends(get_db_service)) -> list[RoleInDB]:
    response = await db.execute(select(Role))
    roles = list(response.scalars().all())
    return roles


@router.patch('/{role_id}',
              response_model=RoleInDB,
              status_code=HTTPStatus.OK,
              description="изменение роли")
async def update_role(
        role_id: str,
        role_create: RoleCreate,
        check_token: Annotated[Token, Depends(check_access_token)],
        check_admin: Annotated[bool, Depends(check_admin_user)],
        db: AsyncSession = Depends(get_db_service)) -> RoleInDB:
    try:
        async with db:
            await check_entity_exists(db, Role, role_id)

            role_exists = await db.execute(
                select(Role).
                filter(Role.title == role_create.title))

            if role_exists.scalars().all():
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail=f"Role {role_create.title} already exists",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        role = await db.get(Role, role_id)
        if role_create.title:
            role.title = role_create.title
        if role_create.permissions:
            role.permissions = role_create.permissions
        await db.commit()
        return RoleInDB(id=role.id,
                        title=role.title,
                        permissions=role.permissions)
    except DBAPIError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'Role with ID: {role_id} not found',
                            headers={"WWW-Authenticate": "Bearer"})


@router.delete('/delete/{role_id}',
               response_model=None,
               status_code=HTTPStatus.NO_CONTENT,
               description="удаление роли")
async def delete_role(
        role_id: str,
        check_token: Annotated[Token, Depends(check_access_token)],
        check_admin: Annotated[bool, Depends(check_admin_user)],
        db: AsyncSession = Depends(get_db_service)):
    try:
        role = await check_entity_exists(db, Role, role_id)

        await db.delete(role)
        await db.commit()
    except DBAPIError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'Role {role_id} not found',
                            headers={"WWW-Authenticate": "Bearer"})
