from typing import Dict, List, Optional
from app.models.user import User, Admin, UserRole
from app.models.ml_model import MLModel
from app.models.transaction import DepositTransaction, WithdrawalTransaction, Transaction
from app.models.prediction import PredictionTask, DataValidator
from app.models.enums import TaskStatus, ModelType

class MLService:
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._models: Dict[str, MLModel] = {}
        self._transactions: List[Transaction] = []
        self._prediction_tasks: Dict[str, PredictionTask] = {}
    
    def register_user(
        self, 
        username: str, 
        email: str, 
        password_hash: str,
        role: UserRole = UserRole.USER
    ) -> User:
        for user in self._users.values():
            if user.username == username:
                raise ValueError(f"Пользователь с именем '{username}' уже существует")
            if user.email == email:
                raise ValueError(f"Пользователь с email '{email}' уже существует")
        
        if role == UserRole.ADMIN:
            user = Admin(username, email, password_hash)
        else:
            user = User(username, email, password_hash, role)
        
        self._users[user.id] = user
        return user
    
    def authenticate_user(self, username: str, password_hash: str) -> Optional[User]:
        for user in self._users.values():
            if (user.username == username and 
                user.password_hash == password_hash and 
                user.is_active):
                return user
        return None
    
    def deposit_funds(self, user_id: str, amount: float) -> Transaction:
        user = self._get_user(user_id)
        transaction = DepositTransaction(user_id, amount)
        transaction.apply(user)
        self._transactions.append(transaction)
        return transaction
    
    def withdraw_funds(self, user_id: str, amount: float, task_id: Optional[str] = None) -> Transaction:
        user = self._get_user(user_id)
        transaction = WithdrawalTransaction(user_id, amount, task_id)
        transaction.apply(user)
        self._transactions.append(transaction)
        return transaction
    
    def _get_user(self, user_id: str) -> User:
        user = self._users.get(user_id)
        if not user:
            raise ValueError(f"Пользователь с ID '{user_id}' не найден")
        return user
    
    def _get_model(self, model_id: str) -> MLModel:
        model = self._models.get(model_id)
        if not model:
            raise ValueError(f"Модель с ID '{model_id}' не найден")
        return model
    
    def add_model(self, model: MLModel) -> None:
        self._models[model.id] = model
    
    def get_available_models(self) -> List[MLModel]:
        return [m for m in self._models.values() if m.is_active]
