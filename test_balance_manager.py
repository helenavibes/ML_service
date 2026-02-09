import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User
from app.models.enums import UserRole, TransactionType
from app.services.balance_manager import BalanceManager


def test_balance_manager_deposit():
    """Тест пополнения баланса"""
    print("🧪 Тест пополнения баланса...")
    
    user = User("test_user", "test@example.com", "hash123", balance=100.0)
    
    # Пополнение
    transaction = BalanceManager.deposit(user, 50.0, "Тестовое пополнение")
    
    assert user.balance == 150.0
    assert transaction.amount == 50.0
    assert transaction.user_id == user.id
    print("✅ Пополнение баланса - OK")
    
    # Отрицательная сумма
    try:
        BalanceManager.deposit(user, -10.0)
        print("❌ Должна быть ошибка при отрицательной сумме")
        return False
    except ValueError as e:
        assert "положительной" in str(e)
        print("✅ Обработка отрицательной суммы - OK")
    
    return True


def test_balance_manager_withdraw():
    """Тест списания баланса"""
    print("\n🧪 Тест списания баланса...")
    
    user = User("test_user", "test@example.com", "hash123", balance=100.0)
    
    # Списание
    transaction = BalanceManager.withdraw(user, 30.0, "Тестовое списание")
    
    assert user.balance == 70.0
    assert transaction.amount == 30.0
    print("✅ Списание баланса - OK")
    
    # Недостаточно средств
    try:
        BalanceManager.withdraw(user, 100.0)
        print("❌ Должна быть ошибка при недостатке средств")
        return False
    except ValueError as e:
        assert "Недостаточно средств" in str(e)
        print("✅ Обработка недостатка средств - OK")
    
    # Отрицательная сумма
    try:
        BalanceManager.withdraw(user, -10.0)
        print("❌ Должна быть ошибка при отрицательной сумме")
        return False
    except ValueError as e:
        assert "положительной" in str(e)
        print("✅ Обработка отрицательной суммы списания - OK")
    
    return True


def test_balance_check():
    """Тест проверки баланса"""
    print("\n🧪 Тест проверки баланса...")
    
    user = User("test_user", "test@example.com", "hash123", balance=100.0)
    
    assert BalanceManager.check_balance(user, 50.0) == True
    assert BalanceManager.check_balance(user, 100.0) == True
    assert BalanceManager.check_balance(user, 150.0) == False
    
    print("✅ Проверка баланса - OK")
    return True


def test_process_payment():
    """Тест обработки платежей"""
    print("\n🧪 Тест обработки платежей...")
    
    user = User("test_user", "test@example.com", "hash123", balance=100.0)
    
    # Пополнение через process_payment
    deposit_transaction = BalanceManager.process_payment(
        user, 50.0, TransactionType.DEPOSIT
    )
    assert user.balance == 150.0
    assert deposit_transaction.amount == 50.0
    
    # Списание через process_payment
    withdrawal_transaction = BalanceManager.process_payment(
        user, 30.0, TransactionType.WITHDRAWAL
    )
    assert user.balance == 120.0
    assert withdrawal_transaction.amount == 30.0
    
    print("✅ Обработка платежей - OK")
    return True


def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование BalanceManager")
    print("=" * 50)
    
    all_passed = True
    
    tests = [
        test_balance_manager_deposit,
        test_balance_manager_withdraw,
        test_balance_check,
        test_process_payment
    ]
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ BALANCEMANAGER ПРОЙДЕНЫ!")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ BALANCEMANAGER")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
