from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from app.models.user import User, Entity
from app.models.enums import TransactionType


class Transaction(Entity):
    def __init__(
            self,
            user_id: str,
            amount: float,
            description: str = "",
            id: Optional[str] = None
    ):
        super().__init__(id)
        self._user_id = user_id
        self._amount = amount
        self._description = description
        self._created_at = datetime.now()

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def description(self) -> str:
        return self._description

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @abstractmethod
    def apply(self, user: User) -> bool:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self._id,
            'user_id': self._user_id,
            'amount': self._amount,
            'description': self._description,
            'created_at': self._created_at.isoformat(),
            'type': self.__class__.__name__
        }


class DepositTransaction(Transaction):
    def __init__(
            self,
            user_id: str,
            amount: float,
            description: str = "Пополнение баланса",
            id: Optional[str] = None
    ):
        super().__init__(user_id, amount, description, id)

    def apply(self, user: User) -> bool:
        return user.deposit(self._amount)


class WithdrawalTransaction(Transaction):
    def __init__(
            self,
            user_id: str,
            amount: float,
            task_id: Optional[str] = None,
            description: str = "Списание за ML предсказание",
            id: Optional[str] = None
    ):
        super().__init__(user_id, amount, description, id)
        self._task_id = task_id

    @property
    def task_id(self) -> Optional[str]:
        return self._task_id

    def apply(self, user: User) -> bool:
        return user.withdraw(self._amount)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        if self._task_id:
            data['task_id'] = self._task_id
        return data