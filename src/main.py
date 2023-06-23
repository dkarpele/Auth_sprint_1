import logging

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import auth, users, roles
from core.config import settings, database_dsn
from core.logger import LOGGING
from db import redis, postgres


async def startup():
    redis.redis = redis.Redis(host=settings.REDIS_HOST,
                              port=settings.REDIS_PORT,
                              ssl=False)
    postgres.postgres = postgres.Postgres(
                      f'postgresql+asyncpg://'
                      f'{database_dsn.user}:{database_dsn.password}@'
                      f'{database_dsn.host}:{database_dsn.port}/'
                      f'{database_dsn.dbname}')
    postgres.get_session()
    await postgres.postgres.create_database()


async def shutdown():
    await redis.redis.close()
    # await postgres.postgres.purge_database()
    await postgres.postgres.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Api for users auth",
    version="1.0.0",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(roles.router, prefix='/api/v1/roles', tags=['roles'])
app.include_router(users.router, prefix='/api/v1/users', tags=['users'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=f'{settings.HOST}',
        port=settings.PORT,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
