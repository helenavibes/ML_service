from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.user import crud_user
from app.crud.ml_model import crud_ml_model
from app.crud.prediction import crud_prediction
from app.crud.transaction import crud_transaction
from app.database.database import get_db
from app.models.db.user import UserDB
from app.models.enums import TaskStatus
from app.schemas.prediction import PredictionRequest, PredictionResponse, PredictionTaskCreate
from app.models.prediction import SimpleDataValidator

router = APIRouter()

@router.post("/", response_model=PredictionResponse)
def create_prediction(
    *,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(deps.get_current_active_user),
    request: PredictionRequest
) -> Any:
    """
    Создание задачи на предсказание
    """
    # Проверка существования модели
    model = crud_ml_model.get(db, id=request.model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    if not model.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model is not active"
        )
    
    # Простая валидация (можно заменить на более сложную)
    validator = SimpleDataValidator(required_fields=["feature1", "feature2"])
    valid_data, invalid_data = validator.validate(request.data)
    
    # Расчет стоимости
    cost = model.calculate_cost(len(valid_data))
    
    # Проверка баланса
    if current_user.balance < cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Required: {cost}, available: {current_user.balance}"
        )
    
    # Создание задачи
    task_in = PredictionTaskCreate(
        user_id=str(current_user.id),
        model_id=request.model_id,
        input_data=request.data
    )
    
    task = crud_prediction.create_with_validation(
        db,
        obj_in=task_in,
        valid_data=valid_data,
        invalid_data=invalid_data
    )
    
    # Если есть валидные данные - запускаем обработку
    if valid_data:
        # Начинаем обработку
        task = crud_prediction.start_processing(db, db_obj=task)
        
        # Имитация предсказания
        result = [f"prediction_{i}" for i in range(len(valid_data))]
        
        # Списание средств
        crud_user.update_balance(db, current_user.id, -cost)
        
        # Создание транзакции
        crud_transaction.create_withdrawal(
            db,
            user_id=current_user.id,
            amount=cost,
            description=f"ML Prediction using {model.name}",
            task_id=task.id
        )
        
        # Завершение задачи
        task = crud_prediction.complete(
            db,
            db_obj=task,
            result=result,
            total_cost=cost
        )
    
    # Формирование ответа - ЯВНОЕ ПРЕОБРАЗОВАНИЕ UUID В СТРОКУ!
    return PredictionResponse(
        task_id=str(task.id),  # ✅ Преобразуем UUID в строку!
        status=task.status,
        model_id=str(model.id),  # ✅ Преобразуем UUID в строку!
        model_name=model.name,
        valid_data_count=len(task.valid_data),
        invalid_data_count=len(task.invalid_data),
        result=task.result if task.status == TaskStatus.COMPLETED else None,
        cost=task.total_cost,
        error_message=task.error_message,
        created_at=task.created_at,
        completed_at=task.completed_at
    )

@router.get("/{task_id}", response_model=PredictionResponse)
def get_prediction(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(deps.get_current_active_user)
) -> Any:
    """
    Получение результата предсказания по ID задачи
    """
    task = crud_prediction.get(db, id=task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction task not found"
        )
    
    # Проверка доступа
    if task.user_id != current_user.id and current_user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Получение имени модели
    model = crud_ml_model.get(db, id=task.model_id)
    model_name = model.name if model else None
    
    # Явное преобразование UUID в строку
    return PredictionResponse(
        task_id=str(task.id),  # ✅ Преобразуем UUID в строку!
        status=task.status,
        model_id=str(task.model_id),  # ✅ Преобразуем UUID в строку!
        model_name=model_name,
        valid_data_count=len(task.valid_data),
        invalid_data_count=len(task.invalid_data),
        result=task.result,
        cost=task.total_cost,
        error_message=task.error_message,
        created_at=task.created_at,
        completed_at=task.completed_at
    )
