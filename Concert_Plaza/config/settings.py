import os
from enum import Enum
from pydantic import Field
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    PROD = 'PROD'
    TEST = 'TEST'
    DEV = 'DEV'


class Settings(BaseSettings):
    
    KINESIS_DATA_STREAM: str = ''
    AWS_ACCESS_KEY: str = ''
    AWS_SECRET_KEY: str = ''
    AWS_REGION: str = ''
    REDIS_HOST: str = ''
    DB_HOST: str = ''
    DB_USERNAME: str = ''
    DB_PASSWORD: str = ''
    DB_DATABASE: str = ''
    DB_PORT: int = 5432

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
