from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.db.prediction import PredictionTaskDB
from app.models.enums import TaskStatus
from pydantic import BaseModel
from datetime import datetime

class PredictionTaskCreate(BaseModel):
    user_id: str
    model_id: str
    input_data: List[Dict[str, Any]]

class PredictionTaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    result: Optional[List[Any]] = None
    error_message: Optional[str] = None
    total_cost: Optional[float] = None

class CRUDPredictionTask(CRUDBase[PredictionTaskDB, PredictionTaskCreate, PredictionTaskUpdate]):
    
    def get_by_user(
        self, db: Session, user_id: str, *, skip: int = 0, limit: int = 100
    ) -> List[PredictionTaskDB]:
        """Получить задачи пользователя"""
        return (
            db.query(self.model)
            .filter(PredictionTaskDB.user_id == user_id)
            .order_by(PredictionTaskDB.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(
        self, db: Session, status: TaskStatus, *, skip: int = 0, limit: int = 100
    ) -> List[PredictionTaskDB]:
        """Получить задачи по статусу"""
        return (
            db.query(self.model)
            .filter(PredictionTaskDB.status == status)
            .order_by(PredictionTaskDB.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_validation(
        self,
        db: Session,
        *,
        obj_in: PredictionTaskCreate,
        valid_data: List[Dict[str, Any]],
        invalid_data: List[Dict[str, Any]]
    ) -> PredictionTaskDB:
        """Создать задачу с результатами валидации"""
        db_obj = PredictionTaskDB(
            user_id=obj_in.user_id,
            model_id=obj_in.model_id,
            input_data=obj_in.input_data,
            valid_data=valid_data,
            invalid_data=invalid_data,
            status=TaskStatus.PENDING if valid_data else TaskStatus.VALIDATION_ERROR
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def start_processing(self, db: Session, *, db_obj: PredictionTaskDB) -> PredictionTaskDB:
        """Начать обработку задачи"""
        db_obj.status = TaskStatus.PROCESSING
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def complete(
        self,
        db: Session,
        *,
        db_obj: PredictionTaskDB,
        result: List[Any],
        total_cost: float
    ) -> PredictionTaskDB:
        """Завершить задачу успешно"""
        db_obj.status = TaskStatus.COMPLETED
        db_obj.result = result
        db_obj.total_cost = total_cost
        db_obj.completed_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def fail(
        self,
        db: Session,
        *,
        db_obj: PredictionTaskDB,
        error_message: str
    ) -> PredictionTaskDB:
        """Завершить задачу с ошибкой"""
        db_obj.status = TaskStatus.FAILED
        db_obj.error_message = error_message
        db_obj.completed_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_status(
        self,
        db: Session,
        *,
        db_obj: PredictionTaskDB,
        status: TaskStatus,
        result: Optional[List[Any]] = None,
        error_message: Optional[str] = None,
        total_cost: Optional[float] = None
    ) -> PredictionTaskDB:
        """Обновить статус задачи"""
        db_obj.status = status
        
        if result is not None:
            db_obj.result = result
        
        if error_message is not None:
            db_obj.error_message = error_message
        
        if total_cost is not None:
            db_obj.total_cost = total_cost
        
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.VALIDATION_ERROR]:
            db_obj.completed_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_prediction = CRUDPredictionTask(PredictionTaskDB)
