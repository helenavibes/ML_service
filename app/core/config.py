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
    
    # База данных - отдельные компоненты
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    
    # Настройки пула соединений
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    
    # RabbitMQ
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    
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
    
    def get_database_url(self) -> str:
        """Формирует URL для подключения к БД из компонентов"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    def get_rabbitmq_url(self) -> str:
        """Формирует URL для подключения к RabbitMQ из компонентов"""
        return f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

settings = Settings()
