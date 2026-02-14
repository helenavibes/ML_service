from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import TaskStatus
from datetime import datetime

class PredictionTaskCreate(BaseModel):
    """Схема для создания задачи предсказания"""
    user_id: str
    model_id: str
    input_data: List[Dict[str, Any]]

class PredictionRequest(BaseModel):
    model_id: str = Field(..., description="ID модели для предсказания")
    data: List[Dict[str, Any]] = Field(..., description="Данные для предсказания")

class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    task_id: str
    status: TaskStatus
    model_id: str
    model_name: Optional[str] = None
    valid_data_count: int
    invalid_data_count: int
    result: Optional[List[Any]] = None
    cost: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class PredictionHistoryItem(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    id: str
    model_id: str
    model_name: Optional[str] = None
    status: TaskStatus
    valid_data_count: int
    invalid_data_count: int
    cost: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
