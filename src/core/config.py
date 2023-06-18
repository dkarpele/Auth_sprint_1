import os
from logging import config as logging_config
from pydantic import BaseSettings, Field

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(..., env='PROJECT_NAME')
    REDIS_HOST: str = Field(..., env='REDIS_HOST')
    REDIS_PORT: int = Field(..., env='REDIS_PORT')
    HOST: str = Field(..., env='HOST')
    PORT: int = Field(..., env='PORT')
    CACHE_EXPIRE_IN_SECONDS: int = Field(..., env='CACHE_EXPIRE_IN_SECONDS')

    class Config:
        env_file = '.env'


settings = Settings()


class DBCreds(BaseSettings):
    dbname: str = Field(..., env="DB_NAME")
    user: str = Field(..., env="DB_USER")
    password: str = Field(..., env="DB_PASSWORD")
    host: str = Field(env="DB_HOST", default='127.0.0.1')
    port: int = Field(env="DB_PORT", default=5432)
    options: str = '-c search_path=%s' % os.environ.get('PG_SCHEMA')

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'


database_dsn = DBCreds()
