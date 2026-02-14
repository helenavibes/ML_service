from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.ml_model import crud_ml_model
from app.database.database import get_db
from app.schemas.model import MLModelResponse

router = APIRouter()

@router.get("/", response_model=List[MLModelResponse])
def get_models(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user)
) -> Any:
    """
    Получение списка всех активных ML моделей
    """
    models = crud_ml_model.get_active_models(db, skip=skip, limit=limit)
    
    # Явное преобразование UUID в строку
    result = []
    for model in models:
        result.append({
            "id": str(model.id),
            "name": model.name,
            "description": model.description,
            "model_type": model.model_type.value if hasattr(model.model_type, 'value') else model.model_type,
            "cost_per_prediction": float(model.cost_per_prediction),
            "is_active": model.is_active,
            "created_at": model.created_at
        })
    
    return result

@router.get("/{model_id}", response_model=MLModelResponse)
def get_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user)
) -> Any:
    """
    Получение информации о конкретной ML модели
    """
    model = crud_ml_model.get(db, id=model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Явное преобразование UUID в строку
    return {
        "id": str(model.id),
        "name": model.name,
        "description": model.description,
        "model_type": model.model_type.value if hasattr(model.model_type, 'value') else model.model_type,
        "cost_per_prediction": float(model.cost_per_prediction),
        "is_active": model.is_active,
        "created_at": model.created_at
    }
