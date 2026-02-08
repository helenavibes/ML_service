from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from app.models.enums import ModelType
from app.models.user import AuditableEntity

class MLModel(AuditableEntity):
    def __init__(
        self,
        name: str,
        description: str,
        model_type: ModelType,
        cost_per_prediction: float,
        is_active: bool = True,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self._name = name
        self._description = description
        self._model_type = model_type
        self._cost_per_prediction = cost_per_prediction
        self._is_active = is_active
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def model_type(self) -> ModelType:
        return self._model_type
    
    @property
    def cost_per_prediction(self) -> float:
        return self._cost_per_prediction
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def calculate_cost(self, data_count: int) -> float:
        return self._cost_per_prediction * data_count
    
    def update_cost(self, new_cost: float) -> None:
        if new_cost <= 0:
            raise ValueError("Стоимость должна быть положительной")
        self._cost_per_prediction = new_cost
        self.update_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self._id,
            'name': self._name,
            'description': self._description,
            'model_type': self._model_type.value,
            'cost_per_prediction': self._cost_per_prediction,
            'is_active': self._is_active,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
