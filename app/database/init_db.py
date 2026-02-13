"""
Скрипт инициализации базы данных
Создает таблицы и заполняет демо-данными
"""

from sqlalchemy.orm import Session
from app.database.database import SessionLocal, init_db as create_tables
from app.models.db.user import UserDB
from app.models.db.ml_model import MLModelDB
from app.models.db.transaction import TransactionDB
from app.models.enums import UserRole, ModelType, TransactionType
from passlib.context import CryptContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_demo_data(db: Session) -> None:
    """Создание демо-пользователей и моделей"""
    
    # 1. Создаем демо-пользователя
    demo_user = db.query(UserDB).filter(UserDB.username == "demo_user").first()
    if not demo_user:
        demo_user = UserDB(
            username="demo_user",
            email="demo@example.com",
            password_hash=pwd_context.hash("demo123"),
            role=UserRole.USER,  # ✅ Используем Enum, не строку!
            balance=100.0,
            is_active=True
        )
        db.add(demo_user)
        db.flush()  # Получаем ID без коммита
        logger.info("✅ Создан демо-пользователь: demo_user")
        
        # Создаем транзакцию пополнения
        transaction = TransactionDB(
            user_id=demo_user.id,
            transaction_type=TransactionType.DEPOSIT,  # ✅ Используем Enum
            amount=100.0,
            description="Начальный баланс"
        )
        db.add(transaction)
        logger.info("✅ Создана транзакция пополнения для demo_user")
    else:
        # Проверяем и исправляем роль если нужно
        if demo_user.role != UserRole.USER:
            demo_user.role = UserRole.USER
            logger.info("✅ Исправлена роль demo_user на USER")
    
    # 2. Создаем администратора
    admin = db.query(UserDB).filter(UserDB.username == "admin").first()
    if not admin:
        admin = UserDB(
            username="admin",
            email="admin@example.com",
            password_hash=pwd_context.hash("admin123"),
            role=UserRole.ADMIN,  # ✅ Используем Enum, не строку!
            balance=1000.0,
            is_active=True
        )
        db.add(admin)
        db.flush()
        logger.info("✅ Создан администратор: admin (role: ADMIN)")
    else:
        # Проверяем и исправляем роль если нужно
        if admin.role != UserRole.ADMIN:
            admin.role = UserRole.ADMIN
            logger.info("✅ Исправлена роль администратора на ADMIN")
    
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
    logger.info("✅ Все изменения сохранены в БД")

def main() -> None:
    """Главная функция инициализации"""
    logger.info("🚀 Начало инициализации базы данных")
    
    create_tables()
    logger.info("✅ Таблицы созданы")
    
    db = SessionLocal()
    try:
        init_demo_data(db)
        logger.info("✅ Демо-данные добавлены")
        
        # Проверка роли администратора
        admin = db.query(UserDB).filter(UserDB.username == "admin").first()
        if admin:
            logger.info(f"✅ Администратор: {admin.username}, роль: {admin.role.value}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    logger.info("🎉 Инициализация базы данных завершена успешно!")

if __name__ == "__main__":
    main()
