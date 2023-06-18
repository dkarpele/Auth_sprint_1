async def _get_cache_key(args_dict: dict = None,
                         index: str = None) -> str:
    if not args_dict:
        args_dict = {}

    key = ''
    for k, v in args_dict.items():
        if v:
            key += f':{k}:{v}'

    return f'index:{index}{key}' if key else f'index:{index}'
