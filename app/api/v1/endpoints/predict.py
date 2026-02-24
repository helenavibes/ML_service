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

    # ВАЛИДАЦИЯ ДАННЫХ
    if not request.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data list is empty"
        )

    # Обрабатываем каждый элемент в списке
    valid_data = []
    invalid_data = []

    for item in request.data:
        # Проверяем наличие полей
        if "x1" in item and "x2" in item:
            try:
                x1 = float(item["x1"])
                x2 = float(item["x2"])
                valid_data.append({"x1": x1, "x2": x2})
            except (ValueError, TypeError):
                invalid_data.append(item)
        else:
            invalid_data.append(item)

    if not valid_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid data items found"
        )

    # Расчет стоимости
    cost = model.calculate_cost(len(valid_data))

    # ПРОВЕРКА БАЛАНСА
    if current_user.balance < cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Required: {cost}, available: {current_user.balance}"
        )

    # Создание задачи - сохраняем ВЕСЬ список валидных данных
    task_in = PredictionTaskCreate(
        user_id=str(current_user.id),
        model_id=request.model_id,
        input_data=valid_data  # Сохраняем весь список
    )

    task = crud_prediction.create_with_validation(
        db,
        obj_in=task_in,
        valid_data=valid_data,
        invalid_data=invalid_data
    )

    # СПИСАНИЕ СРЕДСТВ
    updated_user = crud_user.update_balance(db, current_user.id, -cost)

    # Создание транзакции
    transaction = crud_transaction.create_withdrawal(
        db,
        user_id=current_user.id,
        amount=cost,
        description=f"ML Prediction using {model.name}",
        task_id=task.id
    )

    db.commit()

    return PredictionResponse(
        task_id=str(task.id),
        status=task.status,
        model_id=str(model.id),
        model_name=model.name,
        valid_data_count=len(valid_data),
        invalid_data_count=len(invalid_data),
        result=None,
        cost=cost,
        error_message=None,
        created_at=task.created_at,
        completed_at=None
    )
