from enum import Enum

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATION_ERROR = "validation_error"

class ModelType(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
