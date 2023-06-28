from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import AbstractCache
from models.entity import User
from services.database import get_db_service, get_cache_service
from services.exceptions import entity_doesnt_exist
from services.token import Token, check_access_token
from services.users import get_current_active_user, check_admin_user


DbDep = Annotated[AsyncSession, Depends(get_db_service)]
CacheDep = Annotated[AbstractCache, Depends(get_cache_service)]
TokenDep = Annotated[Token, Depends(check_access_token)]
CurrentUserDep = Annotated[User, Depends(get_current_active_user)]
CheckAdminDep = Annotated[bool, Depends(check_admin_user)]


async def _get_cache_key(args_dict: dict = None,
                         index: str = None) -> str:
    if not args_dict:
        args_dict = {}

    key = ''
    for k, v in args_dict.items():
        if v:
            key += f':{k}:{v}'

    return f'index:{index}{key}' if key else f'index:{index}'


async def check_entity_exists(db: AsyncSession,
                              table,
                              search_value):
    exists = await db.get(table, search_value)
    if not exists:
        raise entity_doesnt_exist(table.__name__, str(search_value))
    return exists
