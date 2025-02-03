from pydantic_settings import BaseSettings
from typing import Optional
import logging


class Settings(BaseSettings):
    PROJECT_NAME: str = "Shopping Mall API"

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    SQL_DEBUG: bool = False

    # Security
    SECRET_KEY: str

    # Log
    LOG_TO_FILE: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


# 로그 설정 함수
def setup_logger(thread_id):
    logger = logging.getLogger(f"ThreadLogger-{thread_id}")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    if settings.LOG_TO_FILE:
        handler = logging.FileHandler(f"thread_log_{thread_id}.log")
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
