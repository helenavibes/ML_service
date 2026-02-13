from enum import Enum

class UserRole(Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    REFUND = "REFUND"

class TaskStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    VALIDATION_ERROR = "VALIDATION_ERROR"

class ModelType(Enum):
    CLASSIFICATION = "CLASSIFICATION"
    REGRESSION = "REGRESSION"
    # CLUSTERING = "CLUSTERING"  # Раскомментировать когда понадобится
