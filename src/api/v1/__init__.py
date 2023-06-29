from sqlalchemy.ext.asyncio import AsyncSession

from services.exceptions import entity_doesnt_exist


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
