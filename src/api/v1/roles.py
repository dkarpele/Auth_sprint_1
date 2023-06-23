from typing import Annotated
from fastapi.encoders import jsonable_encoder

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from services.token import check_access_token_not_valid, oauth2_scheme

from models.roles import Role
from db import AbstractCache
from db.postgres import get_session
from services.database import get_db_service, get_cache_service
from schemas.roles import RoleInDB, RoleCreate

# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.post('/create',
             response_model=RoleInDB,
             status_code=HTTPStatus.CREATED,
             description="создание новой роли",
             response_description="id, title, permissions")
async def create_role(token: Annotated[str, Depends(oauth2_scheme)],
                      role_create: RoleCreate,
                      cache: AbstractCache = Depends(get_cache_service),
                      db: AsyncSession = Depends(get_session)) -> RoleInDB:
    await check_access_token_not_valid(token, cache)
    role_dto = jsonable_encoder(role_create)
    role = Role(**role_dto)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.get('/',
            response_model=list[RoleInDB],
            status_code=HTTPStatus.OK,
            description="просмотр всех ролей")
async def get_all_roles(token: Annotated[str, Depends(oauth2_scheme)],
                        cache: AbstractCache = Depends(get_cache_service),
                        db: AsyncSession = Depends(get_session)) -> list[RoleInDB]:
    await check_access_token_not_valid(token, cache)
    q = select(Role)
    response = await db.execute(q)
    roles = [i for i in response.scalars()]
    return roles


@router.patch('/{role_id}',
              response_model=None,
              status_code=HTTPStatus.OK,
              description="изменение роли")
async def update_role(token: Annotated[str, Depends(oauth2_scheme)],
                      role_id: str, role_create: RoleCreate,
                      cache: AbstractCache = Depends(get_cache_service),
                      db: AsyncSession = Depends(get_session)) -> RoleInDB:
    try:
        await check_access_token_not_valid(token, cache)
        role = await db.get(Role, role_id)
        if role_create.title is not None:
            role.title = role_create.title
        if role_create.permissions is not None:
            role.permissions = role_create.permissions
        await db.commit()
        return RoleInDB(id=role.id, title=role.title, permissions=role.permissions)
    except DBAPIError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'Role not found')


@router.delete('/delete/{role_id}',
               response_model=None,
               status_code=HTTPStatus.NO_CONTENT,
               description="удаление роли")
async def delete_role(token: Annotated[str, Depends(oauth2_scheme)],
                      role_id: str,
                      cache: AbstractCache = Depends(get_cache_service),
                      db: AsyncSession = Depends(get_session)) -> RoleInDB:
    try:
        await check_access_token_not_valid(token, cache)
        role = await db.get(Role, role_id)
        await db.delete(role)
        await db.commit()
        return role
    except DBAPIError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'Role not found')
