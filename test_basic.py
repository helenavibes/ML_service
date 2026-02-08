import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тест импортов основных модулей"""
    print("🧪 Тестирование импортов...")
    
    try:
        from app.models.enums import UserRole, ModelType
        print("✅ app.models.enums - OK")
    except ImportError as e:
        print(f"❌ Ошибка импорта enums: {e}")
        return False
    
    try:
        from app.models.user import User, Admin
        print("✅ app.models.user - OK")
    except ImportError as e:
        print(f"❌ Ошибка импорта user: {e}")
        return False
    
    try:
        from app.models.ml_model import MLModel
        print("✅ app.models.ml_model - OK")
    except ImportError as e:
        print(f"❌ Ошибка импорта ml_model: {e}")
        return False
    
    try:
        from app.services.ml_service import MLService
        print("✅ app.services.ml_service - OK")
    except ImportError as e:
        print(f"❌ Ошибка импорта ml_service: {e}")
        return False
    
    return True

def test_basic_creation():
    """Тест создания базовых объектов"""
    print("\n🧪 Тестирование создания объектов...")
    
    from app.models.user import User
    from app.models.enums import UserRole
    
    user = User(
        username="test_user",
        email="test@example.com",
        password_hash="test_hash"
    )
    
    assert user.username == "test_user"
    assert user.email == "test@example.com"
    assert user.role == UserRole.USER
    assert user.balance == 0.0
    
    print("✅ Создание User - OK")
    
    # Тест пополнения баланса
    user.deposit(100.0)
    assert user.balance == 100.0
    print("✅ Пополнение баланса - OK")
    
    # Тест списания
    user.withdraw(30.0)
    assert user.balance == 70.0
    print("✅ Списание баланса - OK")
    
    return True

def test_ml_model():
    """Тест ML модели"""
    print("\n🧪 Тестирование ML модели...")
    
    from app.models.ml_model import MLModel
    from app.models.enums import ModelType
    
    model = MLModel(
        name="Test Model",
        description="Test Description",
        model_type=ModelType.CLASSIFICATION,
        cost_per_prediction=0.5
    )
    
    assert model.name == "Test Model"
    assert model.cost_per_prediction == 0.5
    assert model.calculate_cost(10) == 5.0
    
    print("✅ Создание MLModel - OK")
    return True

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск базовых тестов проекта")
    print("=" * 50)
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
    
    if all_passed:
        if not test_basic_creation():
            all_passed = False
        
        if not test_ml_model():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
