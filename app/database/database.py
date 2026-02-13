from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator
from app.core.config import settings

# Получаем URL из метода settings
engine = create_engine(
    settings.get_database_url(),
    pool_pre_ping=True,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    echo=settings.DEBUG
)

# Создаем SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Зависимость для получения сессии БД"""
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
