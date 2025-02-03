from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shopping Mall API"
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    SQL_DEBUG: bool = False
    
    # Security
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 