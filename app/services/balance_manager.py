"""
Менеджер баланса пользователя
"""

from typing import Optional
from app.models.user import User
from app.models.transaction import Transaction, DepositTransaction, WithdrawalTransaction
from app.models.enums import TransactionType


class BalanceManager:
    """Класс для управления балансом пользователя"""
    
    @staticmethod
    def check_balance(user: User, required_amount: float) -> bool:
        """
        Проверка достаточности баланса
        :param user: пользователь
        :param required_amount: требуемая сумма
        :return: True если баланс >= required_amount
        """
        return user.balance >= required_amount
    
    @staticmethod
    def get_balance(user: User) -> float:
        """
        Получение текущего баланса
        :param user: пользователь
        :return: текущий баланс
        """
        return user.balance
    
    @staticmethod
    def deposit(user: User, amount: float, description: str = "Пополнение баланса") -> Transaction:
        """
        Пополнение баланса пользователя
        :param user: пользователь
        :param amount: сумма пополнения
        :param description: описание операции
        :return: созданная транзакция
        :raises ValueError: если сумма <= 0
        """
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        
        # Используем метод пользователя для изменения баланса
        user._balance += amount
        user.update_timestamp()
        
        # Создаем транзакцию
        return DepositTransaction(
            user_id=user.id,
            amount=amount,
            description=description
        )
    
    @staticmethod
    def withdraw(user: User, amount: float, description: str = "Списание средств", 
                task_id: Optional[str] = None) -> Transaction:
        """
        Списание средств с баланса пользователя
        :param user: пользователь
        :param amount: сумма списания
        :param description: описание операции
        :param task_id: ID задачи (опционально)
        :return: созданная транзакция
        :raises ValueError: если сумма <= 0 или недостаточно средств
        """
        if amount <= 0:
            raise ValueError("Сумма списания должна быть положительной")
        
        if not BalanceManager.check_balance(user, amount):
            raise ValueError(f"Недостаточно средств. Требуется: {amount}, доступно: {user.balance}")
        
        # Используем метод пользователя для изменения баланса
        user._balance -= amount
        user.update_timestamp()
        
        # Создаем транзакцию
        return WithdrawalTransaction(
            user_id=user.id,
            amount=amount,
            description=description,
            task_id=task_id
        )
    
    @staticmethod
    def process_payment(user: User, amount: float, 
                       transaction_type: TransactionType) -> Transaction:
        """
        Обработка платежа (универсальный метод)
        :param user: пользователь
        :param amount: сумма
        :param transaction_type: тип транзакции
        :return: созданная транзакция
        """
        if transaction_type == TransactionType.DEPOSIT:
            return BalanceManager.deposit(user, amount, "Пополнение баланса")
        elif transaction_type == TransactionType.WITHDRAWAL:
            return BalanceManager.withdraw(user, amount, "Списание средств")
        else:
            raise ValueError(f"Неизвестный тип транзакции: {transaction_type}")
