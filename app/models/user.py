from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from app.models.enums import UserRole


class Entity(ABC):
    """Абстрактный базовый класс для всех сущностей"""
    
    def __init__(self, id: Optional[str] = None):
        """
        Инициализация сущности
        :param id: уникальный идентификатор (генерируется автоматически если не указан)
        """
        self._id = id or str(uuid.uuid4())
    
    @property
    def id(self) -> str:
        """Геттер для ID (только чтение)"""
        return self._id
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта в словарь"""
        pass


class AuditableEntity(Entity):
    """Абстрактный класс для сущностей с временными метками"""
    
    def __init__(self, id: Optional[str] = None):
        """
        Инициализация с временными метками
        :param id: уникальный идентификатор
        """
        super().__init__(id)
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @property
    def created_at(self) -> datetime:
        """Геттер для времени создания"""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """Геттер для времени обновления"""
        return self._updated_at
    
    def update_timestamp(self) -> None:
        """Обновление времени последнего изменения"""
        self._updated_at = datetime.now()


class User(AuditableEntity):
    """Класс пользователя системы"""
    
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
        """
        Инициализация пользователя
        :param username: имя пользователя
        :param email: email
        :param password_hash: хеш пароля
        :param role: роль пользователя
        :param balance: баланс в кредитах
        :param is_active: активен ли пользователь
        :param id: идентификатор
        """
        super().__init__(id)
        self._username = username
        self._email = email
        self._password_hash = password_hash
        self._role = role
        self._balance = balance  # Приватное поле, управление через BalanceManager
        self._is_active = is_active
    
    # ============ PROPERTIES (Свойства) ============
    @property
    def username(self) -> str:
        """Геттер для имени пользователя"""
        return self._username
    
    @property
    def email(self) -> str:
        """Геттер для email"""
        return self._email
    
    @property
    def password_hash(self) -> str:
        """Геттер для хеш пароля"""
        return self._password_hash
    
    @property
    def role(self) -> UserRole:
        """Геттер для роли"""
        return self._role
    
    @property
    def balance(self) -> float:
        """Геттер для баланса (только чтение)"""
        return self._balance
    
    @property
    def is_active(self) -> bool:
        """Геттер для статуса активности"""
        return self._is_active
    
    # ============ PUBLIC METHODS (Публичные методы) ============
    # УБРАНЫ методы deposit() и withdraw() - теперь это ответственность BalanceManager
    
    def deactivate(self) -> None:
        """Деактивация пользователя"""
        self._is_active = False
        self.update_timestamp()
    
    def activate(self) -> None:
        """Активация пользователя"""
        self._is_active = True
        self.update_timestamp()
    
    def change_role(self, new_role: UserRole) -> None:
        """
        Изменение роли пользователя
        :param new_role: новая роль
        """
        self._role = new_role
        self.update_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование пользователя в словарь"""
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
    """Класс администратора (наследуется от User)"""
    
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        balance: float = 0.0,
        is_active: bool = True,
        id: Optional[str] = None
    ):
        """
        Инициализация администратора
        :param username: имя пользователя
        :param email: email
        :param password_hash: хеш пароля
        :param balance: баланс
        :param is_active: активен ли
        :param id: идентификатор
        """
        super().__init__(username, email, password_hash, UserRole.ADMIN, balance, is_active, id)
