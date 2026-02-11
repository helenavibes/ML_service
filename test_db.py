#!/usr/bin/env python3
"""
Тестирование подключения к базе данных и CRUD операций
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal, test_connection
from app.crud.user import crud_user, UserCreate
from app.crud.transaction import crud_transaction
from app.models.db.user import UserDB

def test_connection_db():
    """Тест подключения к БД"""
    print("🧪 Тест 1: Подключение к БД")
    if test_connection():
        print("✅ Подключение успешно")
        return True
    return False

def test_create_user():
    """Тест создания пользователя"""
    print("\n🧪 Тест 2: Создание пользователя")
    db = SessionLocal()
    try:
        # Создаем пользователя
        user_in = UserCreate(
            username="test_user",
            email="test@example.com",
            password="test123",
            balance=50.0
        )
        user = crud_user.create(db, obj_in=user_in)
        print(f"✅ Пользователь создан: {user.username}, ID: {user.id}")
        print(f"   Баланс: {user.balance}")
        
        # Проверка аутентификации
        auth_user = crud_user.authenticate(db, "test_user", "test123")
        if auth_user:
            print(f"✅ Аутентификация успешна")
        else:
            print(f"❌ Аутентификация не удалась")
        
        # Очистка
        db.delete(user)
        db.commit()
        print("✅ Тестовый пользователь удален")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        db.close()

def test_balance():
    """Тест операций с балансом"""
    print("\n🧪 Тест 3: Операции с балансом")
    db = SessionLocal()
    try:
        # Создаем пользователя
        user_in = UserCreate(
            username="balance_test",
            email="balance@test.com",
            password="test123",
            balance=100.0
        )
        user = crud_user.create(db, obj_in=user_in)
        print(f"✅ Создан пользователь с балансом: {user.balance}")
        
        # Пополнение баланса - создаем транзакцию и обновляем баланс
        deposit = crud_transaction.create_deposit(
            db, user_id=user.id, amount=50.0, description="Тестовое пополнение"
        )
        user = crud_user.update_balance(db, user.id, 50.0)
        print(f"✅ Пополнение +50: {user.balance}")
        print(f"   Транзакция: {deposit.id}, сумма: {deposit.amount}")
        
        # Списание - создаем транзакцию и обновляем баланс
        withdrawal = crud_transaction.create_withdrawal(
            db, user_id=user.id, amount=30.0, description="Тестовое списание"
        )
        user = crud_user.update_balance(db, user.id, -30.0)
        print(f"✅ Списание -30: {user.balance}")
        print(f"   Транзакция: {withdrawal.id}, сумма: {withdrawal.amount}")
        
        # Проверка транзакций
        transactions = crud_transaction.get_by_user(db, user.id)
        print(f"✅ Транзакций пользователя: {len(transactions)}")
        
        # Вывод информации о транзакциях
        for t in transactions:
            print(f"   - {t.transaction_type.value}: {t.amount}, {t.description}")
        
        # Очистка
        for t in transactions:
            db.delete(t)
        db.delete(user)
        db.commit()
        print("✅ Тестовые данные удалены")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """Главная функция тестирования"""
    print("=" * 50)
    print("🚀 ТЕСТИРОВАНИЕ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    tests = [
        ("Подключение к БД", test_connection_db),
        ("Создание пользователя", test_create_user),
        ("Операции с балансом", test_balance),
    ]
    
    results = []
    for name, test in tests:
        print(f"\n--- {name} ---")
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"   Пройдено: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("   База данных работает корректно")
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
