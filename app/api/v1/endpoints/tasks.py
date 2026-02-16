import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.database.database import get_db
from app.models.db.user import UserDB
from app.models.db.prediction import PredictionTaskDB
from app.models.enums import TaskStatus
from app.queue.rabbitmq import rabbitmq_client
from app.schemas.task import MLTaskCreate, MLTaskResponse, MLTaskMessage
from app.crud.ml_model import crud_ml_model
from app.crud.prediction import crud_prediction

router = APIRouter()

@router.post("/", response_model=MLTaskResponse)
async def create_ml_task(
    *,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(deps.get_current_active_user),
    task_in: MLTaskCreate
) -> Any:
    """
    Создание асинхронной ML задачи
    """
    # Проверка существования модели
    model = crud_ml_model.get(db, id=task_in.model_id)
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
    
    # Создаем задачу в БД
    task_id = str(uuid.uuid4())
    db_task = PredictionTaskDB(
        id=task_id,
        user_id=current_user.id,
        model_id=model.id,
        status=TaskStatus.PENDING,
        input_data=[task_in.features]  # Сохраняем как массив
    )
    db.add(db_task)
    db.commit()
    
    # Формируем сообщение для RabbitMQ - ЯВНОЕ ПРЕОБРАЗОВАНИЕ UUID В СТРОКУ!
    message = MLTaskMessage(
        task_id=task_id,
        model_id=str(model.id),  # ✅ Преобразуем UUID в строку!
        features=task_in.features,
        timestamp=datetime.utcnow()
    )
    
    # Отправляем в очередь
    success = rabbitmq_client.publish(message.dict())
    if not success:
        # Если не удалось отправить, помечаем задачу как failed
        db_task.status = TaskStatus.FAILED
        db_task.error_message = "Failed to publish to queue"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to create task"
        )
    
    return MLTaskResponse(
        task_id=task_id,
        status=db_task.status,
        created_at=db_task.created_at
    )

@router.get("/{task_id}", response_model=MLTaskResponse)
def get_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(deps.get_current_active_user)
) -> Any:
    """
    Получение статуса задачи
    """
    task = db.query(PredictionTaskDB).filter(PredictionTaskDB.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Проверка доступа
    if task.user_id != current_user.id and current_user.role != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return MLTaskResponse(
        task_id=task.id,
        status=task.status,
        created_at=task.created_at
    )
