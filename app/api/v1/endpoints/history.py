from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.prediction import crud_prediction
from app.crud.transaction import crud_transaction
from app.crud.ml_model import crud_ml_model
from app.database.database import get_db
from app.models.db.user import UserDB
from app.schemas.prediction import PredictionHistoryItem
from app.schemas.transaction import TransactionResponse

router = APIRouter()

@router.get("/predictions", response_model=List[PredictionHistoryItem])
def get_prediction_history(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Получение истории предсказаний пользователя
    """
    tasks = crud_prediction.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    
    result = []
    for task in tasks:
        model = crud_ml_model.get(db, id=task.model_id)
        # Явное преобразование UUID в строку!
        result.append({
            "id": str(task.id),
            "model_id": str(task.model_id),
            "model_name": model.name if model else None,
            "status": task.status,
            "valid_data_count": len(task.valid_data),
            "invalid_data_count": len(task.invalid_data),
            "cost": task.total_cost,
            "created_at": task.created_at,
            "completed_at": task.completed_at
        })
    
    return result

@router.get("/transactions", response_model=List[TransactionResponse])
def get_transaction_history(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Получение истории транзакций пользователя
    """
    transactions = crud_transaction.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    # Явное преобразование UUID в строку для транзакций
    result = []
    for t in transactions:
        result.append({
            "id": str(t.id),
            "user_id": str(t.user_id),
            "transaction_type": t.transaction_type,
            "amount": float(t.amount),
            "description": t.description,
            "task_id": str(t.task_id) if t.task_id else None,
            "created_at": t.created_at
        })
    return result
