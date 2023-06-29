from logging import config as logging_config

from utils.logger import LOGGING
from settings import database_dsn

from utils.backoff import backoff, BackoffError
from src.db import postgres
# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


@backoff(service='Postgres')
async def wait_postgres():
    postgres.postgres = postgres.Postgres(
                      f'postgresql+asyncpg://'
                      f'{database_dsn.user}:{database_dsn.password}@'
                      f'{database_dsn.host}:{database_dsn.port}/'
                      f'{database_dsn.dbname}')

    if not postgres.get_session():
        raise BackoffError()
    await postgres.postgres.create_database()
