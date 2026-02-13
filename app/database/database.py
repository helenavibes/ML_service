from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator
from app.core.config import settings

# Берем настройки из конфига!
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.POOL_SIZE if hasattr(settings, 'POOL_SIZE') else 5,
    max_overflow=settings.MAX_OVERFLOW if hasattr(settings, 'MAX_OVERFLOW') else 10,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    from app.models.db.base import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы успешно")

def drop_db() -> None:
    from app.models.db.base import Base
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Таблицы удалены")

def test_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
