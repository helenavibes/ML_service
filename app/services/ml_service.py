from typing import Dict, List, Optional
from app.models.user import User, Admin, UserRole
from app.models.ml_model import MLModel
from app.models.transaction import Transaction
from app.models.prediction import PredictionTask, DataValidator, SimpleDataValidator
from app.models.enums import TaskStatus, ModelType
from app.services.balance_manager import BalanceManager


class MLService:
    """Основной сервис ML платформы"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._models: Dict[str, MLModel] = {}
        self._transactions: List[Transaction] = []
        self._prediction_tasks: Dict[str, PredictionTask] = {}
        self._balance_manager = BalanceManager()
    
    # ============ USER METHODS ============
    def register_user(
        self, 
        username: str, 
        email: str, 
        password_hash: str,
        role: UserRole = UserRole.USER
    ) -> User:
        """
        Регистрация нового пользователя
        :return: созданный пользователь
        :raises ValueError: если пользователь с таким именем/email уже существует
        """
        # Проверка уникальности
        for user in self._users.values():
            if user.username == username:
                raise ValueError(f"Пользователь с именем '{username}' уже существует")
            if user.email == email:
                raise ValueError(f"Пользователь с email '{email}' уже существует")
        
        # Создание пользователя
        if role == UserRole.ADMIN:
            user = Admin(username, email, password_hash)
        else:
            user = User(username, email, password_hash, role)
        
        self._users[user.id] = user
        return user
    
    def authenticate_user(self, username: str, password_hash: str) -> Optional[User]:
        """
        Аутентификация пользователя
        :return: пользователь или None
        """
        for user in self._users.values():
            if (user.username == username and 
                user.password_hash == password_hash and 
                user.is_active):
                return user
        return None
    
    # ============ BALANCE METHODS (через BalanceManager) ============
    def deposit_funds(self, user_id: str, amount: float, description: str = "") -> Transaction:
        """
        Пополнение баланса пользователя
        :return: созданная транзакция
        :raises ValueError: если пользователь не найден
        """
        user = self._get_user(user_id)
        
        # Используем BalanceManager для пополнения
        transaction = self._balance_manager.deposit(
            user=user,
            amount=amount,
            description=description or "Пополнение баланса через систему"
        )
        
        self._transactions.append(transaction)
        return transaction
    
    def withdraw_funds(self, user_id: str, amount: float, 
                      description: str = "", task_id: Optional[str] = None) -> Transaction:
        """
        Списание средств с баланса пользователя
        :return: созданная транзакция
        :raises ValueError: если пользователь не найден или недостаточно средств
        """
        user = self._get_user(user_id)
        
        # Используем BalanceManager для списания
        transaction = self._balance_manager.withdraw(
            user=user,
            amount=amount,
            description=description or "Списание средств через систему",
            task_id=task_id
        )
        
        self._transactions.append(transaction)
        return transaction
    
    def check_user_balance(self, user_id: str, required_amount: float) -> bool:
        """
        Проверка достаточности баланса пользователя
        :return: True если баланс >= required_amount
        """
        user = self._get_user(user_id)
        return self._balance_manager.check_balance(user, required_amount)
    
    def get_user_balance(self, user_id: str) -> float:
        """
        Получение баланса пользователя
        :return: текущий баланс
        """
        user = self._get_user(user_id)
        return self._balance_manager.get_balance(user)
    
    # ============ PREDICTION METHODS ============
    def create_prediction_task(
        self,
        user_id: str,
        model_id: str,
        input_data: List[Dict[str, Any]],
        validator: Optional[DataValidator] = None
    ) -> PredictionTask:
        """
        Создание задачи на предсказание
        :return: созданная задача
        :raises ValueError: если пользователь или модель не найдены, или недостаточно средств
        """
        user = self._get_user(user_id)
        model = self._get_model(model_id)
        
        # Создание задачи
        task = PredictionTask(user_id, model_id, input_data)
        
        # Валидация данных
        if validator:
            valid_data, invalid_data = validator.validate(input_data)
            task.set_validated_data(valid_data, invalid_data)
            
            if not valid_data:
                task.mark_validation_error()
                self._prediction_tasks[task.id] = task
                return task
        else:
            # Если валидатора нет, считаем все данные валидными
            task.set_validated_data(input_data, [])
        
        # Проверка баланса (только для валидных данных)
        cost = model.calculate_cost(len(task.valid_data))
        if not self.check_user_balance(user_id, cost):
            raise ValueError(f"Недостаточно средств. Требуется: {cost}, доступно: {user.balance}")
        
        # Резервирование средств
        self.withdraw_funds(
            user_id=user_id,
            amount=cost,
            description=f"Оплата ML предсказания (модель: {model.name})",
            task_id=task.id
        )
        
        task.start_processing()
        self._prediction_tasks[task.id] = task
        
        return task
    
    # ============ PRIVATE METHODS ============
    def _get_user(self, user_id: str) -> User:
        """Получение пользователя по ID"""
        user = self._users.get(user_id)
        if not user:
            raise ValueError(f"Пользователь с ID '{user_id}' не найден")
        return user
    
    def _get_model(self, model_id: str) -> MLModel:
        """Получение модели по ID"""
        model = self._models.get(model_id)
        if not model:
            raise ValueError(f"Модель с ID '{model_id}' не найден")
        return model
    
    # ============ MODEL MANAGEMENT ============
    def add_model(self, model: MLModel) -> None:
        """Добавление модели в сервис"""
        self._models[model.id] = model
    
    def get_available_models(self) -> List[MLModel]:
        """Получение списка доступных моделей"""
        return [m for m in self._models.values() if m.is_active]
    
    # ============ HISTORY METHODS ============
    def get_user_transactions(self, user_id: str) -> List[Transaction]:
        """Получение транзакций пользователя"""
        return [t for t in self._transactions if t.user_id == user_id]
    
    def get_user_prediction_history(self, user_id: str) -> List[PredictionTask]:
        """Получение истории предсказаний пользователя"""
        return [t for t in self._prediction_tasks.values() if t.user_id == user_id]
    
    # ============ ADMIN METHODS ============
    def admin_replenish_balance(
        self,
        admin_user_id: str,
        target_user_id: str,
        amount: float
    ) -> Transaction:
        """
        Пополнение баланса пользователя администратором
        :return: созданная транзакция
        """
        admin = self._get_user(admin_user_id)
        if admin.role != UserRole.ADMIN:
            raise ValueError("Требуются права администратора")
        
        target_user = self._get_user(target_user_id)
        
        # Используем BalanceManager через публичный метод
        transaction = self.deposit_funds(
            user_id=target_user_id,
            amount=amount,
            description=f"Пополнение администратором {admin.username}"
        )
        
        return transaction
