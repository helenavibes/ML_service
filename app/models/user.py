from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from app.models.enums import UserRole

class Entity(ABC):
    def __init__(self, id: Optional[str] = None):
        self._id = id or str(uuid.uuid4())
    
    @property
    def id(self) -> str:
        return self._id
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

class AuditableEntity(Entity):
    def __init__(self, id: Optional[str] = None):
        super().__init__(id)
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def update_timestamp(self) -> None:
        self._updated_at = datetime.now()

class User(AuditableEntity):
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
        balance: float = 0.0,
        is_active: bool = True,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self._username = username
        self._email = email
        self._password_hash = password_hash
        self._role = role
        self._balance = balance
        self._is_active = is_active
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def password_hash(self) -> str:
        return self._password_hash
    
    @property
    def role(self) -> UserRole:
        return self._role
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self._balance += amount
        self.update_timestamp()
        return True
    
    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма списания должна быть положительной")
        if self._balance < amount:
            raise ValueError("Недостаточно средств на балансе")
        self._balance -= amount
        self.update_timestamp()
        return True
    
    def has_sufficient_balance(self, amount: float) -> bool:
        return self._balance >= amount
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self._id,
            'username': self._username,
            'email': self._email,
            'role': self._role.value,
            'balance': self._balance,
            'is_active': self._is_active,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }

class Admin(User):
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        balance: float = 0.0,
        is_active: bool = True,
        id: Optional[str] = None
    ):
        super().__init__(username, email, password_hash, UserRole.ADMIN, balance, is_active, id)
    
    def replenish_user_balance(self, user: User, amount: float) -> bool:
        return user.deposit(amount)
