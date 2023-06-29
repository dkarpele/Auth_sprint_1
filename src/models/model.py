import orjson

from fastapi import Query
from pydantic import BaseModel

import src.core.config as conf


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Model(BaseModel):
    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True


class TokenCache(Model):
    token: str
    data: str


class PaginateModel:
    def __init__(self,
                 page_number: int = Query(1,
                                          description=conf.PAGE_DESC,
                                          ge=1,
                                          le=10000),
                 page_size: int = Query(50,
                                        description=conf.SIZE_DESC,
                                        ge=1,
                                        le=500),
                 ):
        self.page_number = page_number
        self.page_size = page_size
