import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User, UserRole, Admin
from app.models.ml_model import MLModel
from app.models.enums import ModelType
from app.services.ml_service import MLService


def main():
    print("=" * 50)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ ML СЕРВИСА")
    print("=" * 50)

    # Создаем сервис
    service = MLService()
    print("✅ Сервис создан")

    # Регистрируем обычного пользователя
    try:
        user = service.register_user(
            username="ivan_ivanov",
            email="ivan@example.com",
            password_hash="hashed_password_123"
        )
        print(f"✅ Пользователь зарегистрирован: {user.username}")
        print(f"   ID: {user.id}")
        print(f"   Баланс: {user.balance}")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")

    # Регистрируем администратора
    try:
        admin = service.register_user(
            username="admin",
            email="admin@example.com",
            password_hash="admin_hash",
            role=UserRole.ADMIN
        )
        print(f"✅ Администратор зарегистрирован: {admin.username}")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")

    # Пополняем баланс
    print("\n--- Пополнение баланса ---")
    try:
        transaction = service.deposit_funds(user.id, 100.0)
        print(f"✅ Баланс пополнен на {transaction.amount}")
        print(f"   Текущий баланс: {user.balance}")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")

    # Создаем ML модель
    print("\n--- Создание ML модели ---")
    model = MLModel(
        name="Классификатор текста",
        description="Классификация текстовых данных по категориям",
        model_type=ModelType.CLASSIFICATION,
        cost_per_prediction=0.5
    )
    service.add_model(model)
    print(f"✅ Модель создана: {model.name}")
    print(f"   Тип: {model.model_type.value}")
    print(f"   Стоимость предсказания: {model.cost_per_prediction}")
    print(f"   Стоимость 10 предсказаний: {model.calculate_cost(10)}")

    # Аутентификация
    print("\n--- Аутентификация ---")
    auth_user = service.authenticate_user("ivan_ivanov", "hashed_password_123")
    if auth_user:
        print(f"✅ Пользователь аутентифицирован: {auth_user.username}")
    else:
        print("❌ Ошибка аутентификации")

    # Попытка аутентификации с неправильным паролем
    wrong_auth = service.authenticate_user("ivan_ivanov", "wrong_password")
    if not wrong_auth:
        print("✅ Корректная обработка неправильного пароля")

    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 50)


if __name__ == "__main__":
    main()