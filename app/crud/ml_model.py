from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.db.ml_model import MLModelDB
from pydantic import BaseModel
from app.models.enums import ModelType

class MLModelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    model_type: ModelType
    cost_per_prediction: float
    is_active: bool = True

class MLModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[ModelType] = None
    cost_per_prediction: Optional[float] = None
    is_active: Optional[bool] = None

class CRUDMLModel(CRUDBase[MLModelDB, MLModelCreate, MLModelUpdate]):
    
    def get_by_name(self, db: Session, name: str) -> Optional[MLModelDB]:
        """Получить модель по имени"""
        return db.query(MLModelDB).filter(MLModelDB.name == name).first()
    
    def get_active_models(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[MLModelDB]:
        """Получить все активные модели"""
        return (
            db.query(MLModelDB)
            .filter(MLModelDB.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_type(
        self, db: Session, model_type: ModelType
    ) -> List[MLModelDB]:
        """Получить модели по типу"""
        return (
            db.query(MLModelDB)
            .filter(MLModelDB.model_type == model_type)
            .all()
        )
    
    def calculate_cost(self, model: MLModelDB, data_count: int) -> float:
        """Рассчитать стоимость предсказаний"""
        return model.cost_per_prediction * data_count

crud_ml_model = CRUDMLModel(MLModelDB)
