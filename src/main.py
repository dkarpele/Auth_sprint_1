import logging

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import registration
from core.config import settings
from core.logger import LOGGING
from db import redis, postgres


async def startup():
    redis.redis = redis.Redis(host=settings.REDIS_HOST,
                              port=settings.REDIS_PORT,
                              ssl=False)

    await postgres.create_database()


async def shutdown():
    await redis.redis.close()


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

app.include_router(registration.router, prefix='/api/v1/user', tags=['user'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=f'{settings.HOST}',
        port=settings.PORT,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
