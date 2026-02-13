from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Основные настройки
    PROJECT_NAME: str = "ML Service Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_STR: str = "/api/v1"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # База данных
    DATABASE_URL: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    
    # Настройки пула соединений
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    
    # RabbitMQ
    RABBITMQ_URL: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis (кеширование)
    REDIS_URL: Optional[str] = None
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
