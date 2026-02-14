from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.user import crud_user
from app.crud.transaction import crud_transaction
from app.database.database import get_db
from app.models.db.user import UserDB
from app.schemas.balance import BalanceResponse, DepositRequest, DepositResponse

router = APIRouter()

@router.get("/", response_model=BalanceResponse)
def get_balance(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(deps.get_current_active_user)
) -> Any:
    """
    Получение текущего баланса пользователя
    """
    # Явное преобразование UUID в строку
    return BalanceResponse(
        balance=float(current_user.balance),
        user_id=str(current_user.id),  # ✅ Преобразуем UUID в строку!
        username=current_user.username
    )

@router.post("/deposit", response_model=DepositResponse)
def deposit(
    *,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(deps.get_current_active_user),
    deposit_in: DepositRequest
) -> Any:
    """
    Пополнение баланса пользователя
    """
    # Обновление баланса пользователя
    user = crud_user.update_balance(
        db, 
        user_id=current_user.id, 
        amount=deposit_in.amount
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Создание транзакции пополнения
    transaction = crud_transaction.create_deposit(
        db,
        user_id=current_user.id,
        amount=deposit_in.amount,
        description=deposit_in.description
    )
    
    # Явное преобразование UUID в строку
    return DepositResponse(
        transaction_id=str(transaction.id),
        user_id=str(current_user.id),
        amount=deposit_in.amount,
        new_balance=float(user.balance),
        description=transaction.description,
        created_at=transaction.created_at
    )
