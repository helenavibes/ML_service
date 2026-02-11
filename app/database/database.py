from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator
import os

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://ml_user:ml_password@localhost:5432/ml_service"
)

# Создаем engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False
)

# Создаем SessionLocal класс
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Зависимость для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Создание таблиц в базе данных"""
    from app.models.db.base import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы успешно")

def drop_db() -> None:
    """Удаление всех таблиц (только для тестов)"""
    from app.models.db.base import Base
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Таблицы удалены")

def test_connection() -> bool:
    """Тест подключения к базе данных"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
