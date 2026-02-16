from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.enums import TaskStatus

class MLTaskCreate(BaseModel):
    """Создание ML задачи"""
    model_id: str
    features: Dict[str, Any] = Field(..., description="Входные данные для ML модели")
    
class MLTaskResponse(BaseModel):
    """Ответ с информацией о задаче"""
    task_id: str
    status: TaskStatus
    created_at: datetime
    
class MLTaskResult(BaseModel):
    """Результат обработки задачи"""
    task_id: str
    prediction: Any
    worker_id: str
    status: TaskStatus
    completed_at: datetime
    error: Optional[str] = None
    
class MLTaskMessage(BaseModel):
    """Сообщение для RabbitMQ"""
    task_id: str
    model_id: str
    features: Dict[str, Any]
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
