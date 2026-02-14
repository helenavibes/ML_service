from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import ModelType
from datetime import datetime

class MLModelResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True, arbitrary_types_allowed=True)
    
    id: str
    name: str
    description: Optional[str] = None
    model_type: ModelType
    cost_per_prediction: float
    is_active: bool
    created_at: datetime
    
    @classmethod
    def from_orm(cls, obj):
        """Преобразование из ORM объекта"""
        return cls(
            id=str(obj.id),
            name=obj.name,
            description=obj.description,
            model_type=obj.model_type,
            cost_per_prediction=float(obj.cost_per_prediction),
            is_active=obj.is_active,
            created_at=obj.created_at
        )
