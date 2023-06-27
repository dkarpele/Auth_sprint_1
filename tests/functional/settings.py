import os
from logging import config as logging_config
from pydantic import BaseSettings, Field

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field(..., env='PROJECT_NAME')
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: int = Field(..., env='REDIS_PORT')
    service_url: str = Field('http://0.0.0.0:8000', env='SERVICE_URL')

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
