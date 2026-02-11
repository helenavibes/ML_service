"""
Скрипт инициализации базы данных
Создает таблицы и заполняет демо-данными
"""

from sqlalchemy.orm import Session
from app.database.database import SessionLocal, init_db as create_tables
from app.crud.user import crud_user, UserCreate
from app.crud.transaction import crud_transaction
from app.models.db.ml_model import MLModelDB
from app.models.enums import ModelType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_demo_data(db: Session) -> None:
    """Создание демо-пользователей и моделей"""
    
    # 1. Создаем демо-пользователя
    demo_user = crud_user.get_by_username(db, username="demo_user")
    if not demo_user:
        user_in = UserCreate(
            username="demo_user",
            email="demo@example.com",
            password="demo123",
            balance=100.0
        )
        demo_user = crud_user.create(db, obj_in=user_in)
        logger.info("✅ Создан демо-пользователь: demo_user")
        
        # Создаем транзакцию пополнения
        crud_transaction.create_deposit(
            db,
            user_id=demo_user.id,
            amount=100.0,
            description="Начальный баланс"
        )
    
    # 2. Создаем администратора
    admin = crud_user.get_by_username(db, username="admin")
    if not admin:
        admin_in = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123",
            balance=1000.0
        )
        admin = crud_user.create(db, obj_in=admin_in)
        logger.info("✅ Создан администратор: admin")
    
    # 3. Создаем ML модели
    models = [
        {
            "name": "Классификатор текста",
            "description": "Модель для классификации текстовых документов",
            "model_type": ModelType.CLASSIFICATION,
            "cost_per_prediction": 0.5
        },
        {
            "name": "Прогнозирование цен",
            "description": "Модель регрессии для прогнозирования цен",
            "model_type": ModelType.REGRESSION,
            "cost_per_prediction": 1.0
        },
        {
            "name": "Анализ тональности",
            "description": "Определение тональности текста",
            "model_type": ModelType.CLASSIFICATION,
            "cost_per_prediction": 0.3
        }
    ]
    
    for model_data in models:
        model = db.query(MLModelDB).filter(
            MLModelDB.name == model_data["name"]
        ).first()
        
        if not model:
            model = MLModelDB(**model_data)
            db.add(model)
            logger.info(f"✅ Создана ML модель: {model_data['name']}")
    
    db.commit()

def main() -> None:
    """Главная функция инициализации"""
    logger.info("🚀 Начало инициализации базы данных")
    
    # 1. Создаем таблицы
    create_tables()
    logger.info("✅ Таблицы созданы")
    
    # 2. Создаем сессию и заполняем данными
    db = SessionLocal()
    try:
        init_demo_data(db)
        logger.info("✅ Демо-данные добавлены")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    logger.info("🎉 Инициализация базы данных завершена успешно!")

if __name__ == "__main__":
    main()
