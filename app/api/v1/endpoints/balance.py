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
    try:
        return BalanceResponse(
            balance=float(current_user.balance),
            user_id=str(current_user.id),
            username=current_user.username
        )
    except Exception as e:
        print(f"Get balance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
    try:
        if deposit_in.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be positive"
            )
        
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
            description=deposit_in.description or "Пополнение баланса"
        )
        
        db.commit()
        
        return DepositResponse(
            transaction_id=str(transaction.id),
            user_id=str(current_user.id),
            amount=deposit_in.amount,
            new_balance=float(user.balance),
            description=transaction.description,
            created_at=transaction.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Deposit error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
