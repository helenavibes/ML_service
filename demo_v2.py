#!/usr/bin/env python3
"""
Демонстрационный скрипт для ML сервиса (версия 2)
С разделением ответственности - BalanceManager управляет балансом
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User, UserRole, Admin
from app.models.ml_model import MLModel
from app.models.enums import ModelType, TransactionType
from app.services.ml_service import MLService
from app.services.balance_manager import BalanceManager


def demonstrate_separation_of_concerns():
    """Демонстрация разделения ответственности"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ: РАЗДЕЛЕНИЕ ОТВЕТСТВЕННОСТИ (BalanceManager)")
    print("=" * 60)
    
    # Создаем пользователя
    user = User("alice", "alice@example.com", "hash123", balance=200.0)
    print(f"Создан пользователь: {user.username}")
    print(f"Начальный баланс: {user.balance}")
    
    # Демонстрация: User НЕ имеет методов управления балансом
    print("\n1. Проверка инкапсуляции User:")
    print(f"   user.balance (getter): {user.balance}")
    print("   user.deposit() - МЕТОД УДАЛЕН (правильно!)")
    print("   user.withdraw() - МЕТОД УДАЛЕН (правильно!)")
    
    # Используем BalanceManager
    print("\n2. Использование BalanceManager:")
    
    # Пополнение через BalanceManager
    transaction1 = BalanceManager.deposit(user, 100.0, "Пополнение через BalanceManager")
    print(f"   Пополнение +100: баланс = {user.balance}")
    print(f"   Создана транзакция: {transaction1.description}")
    
    # Списание через BalanceManager
    transaction2 = BalanceManager.withdraw(user, 50.0, "Списание через BalanceManager")
    print(f"   Списание -50: баланс = {user.balance}")
    print(f"   Создана транзакция: {transaction2.description}")
    
    # Проверка баланса
    can_afford = BalanceManager.check_balance(user, 100.0)
    print(f"   Может ли оплатить 100? {can_afford}")
    
    # Универсальный метод
    transaction3 = BalanceManager.process_payment(user, 25.0, TransactionType.DEPOSIT)
    print(f"   Универсальное пополнение +25: баланс = {user.balance}")
    
    print("\n✅ Управление балансом вынесено в отдельную сущность BalanceManager")
    print("   Принцип единственной ответственности (Single Responsibility Principle)")


def demonstrate_ml_service_integration():
    """Демонстрация интеграции с MLService"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ: ИНТЕГРАЦИЯ С MLSERVICE")
    print("=" * 60)
    
    service = MLService()
    
    # Регистрация пользователя
    user = service.register_user("bob", "bob@example.com", "pass123")
    print(f"Зарегистрирован пользователь: {user.username}")
    
    # Пополнение через сервис (который использует BalanceManager)
    transaction = service.deposit_funds(user.id, 500.0, "Начальное пополнение")
    print(f"Пополнение через сервис: +{transaction.amount}")
    print(f"Баланс через сервис: {service.get_user_balance(user.id)}")
    
    # Проверка баланса через сервис
    can_afford_300 = service.check_user_balance(user.id, 300.0)
    can_afford_600 = service.check_user_balance(user.id, 600.0)
    print(f"Может оплатить 300? {can_afford_300}")
    print(f"Может оплатить 600? {can_afford_600}")
    
    # Создание модели
    model = MLModel(
        name="Премиум классификатор",
        description="Продвинутая модель для классификации",
        model_type=ModelType.CLASSIFICATION,
        cost_per_prediction=10.0
    )
    service.add_model(model)
    
    print(f"\nСоздана модель: {model.name}")
    print(f"Стоимость предсказания: {model.cost_per_prediction}")
    
    print("\n✅ MLService использует BalanceManager для управления балансом")
    print("   Четкое разделение ответственности")


def main():
    """Основная функция демонстрации"""
    print("🚀 ДЕМОНСТРАЦИЯ ОБНОВЛЕННОЙ ОБЪЕКТНОЙ МОДЕЛИ")
    print("   с выделением BalanceManager как отдельной сущности")
    print("=" * 60)
    
    demonstrate_separation_of_concerns()
    demonstrate_ml_service_integration()
    
    print("\n" + "=" * 60)
    print("ИТОГИ РЕФАКТОРИНГА:")
    print("1. ✅ Удалены методы deposit() и withdraw() из класса User")
    print("2. ✅ Создан отдельный класс BalanceManager")
    print("3. ✅ BalanceManager отвечает ТОЛЬКО за управление балансом")
    print("4. ✅ User отвечает ТОЛЬКО за данные пользователя")
    print("5. ✅ MLService использует BalanceManager для операций с балансом")
    print("6. ✅ Соблюден принцип единственной ответственности (SRP)")
    print("=" * 60)


if __name__ == "__main__":
    main()
