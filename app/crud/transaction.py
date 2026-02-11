from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.db.transaction import TransactionDB
from app.models.enums import TransactionType
from pydantic import BaseModel

class TransactionCreate(BaseModel):
    user_id: str
    amount: float
    description: Optional[str] = None
    task_id: Optional[str] = None

class CRUDTransaction(CRUDBase[TransactionDB, TransactionCreate, TransactionCreate]):
    
    def get_by_user(
        self, db: Session, user_id: str, *, skip: int = 0, limit: int = 100
    ) -> List[TransactionDB]:
        return (
            db.query(self.model)
            .filter(TransactionDB.user_id == user_id)
            .order_by(TransactionDB.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_deposit(
        self, db: Session, *, user_id: str, amount: float, description: str = ""
    ) -> TransactionDB:
        """Создание транзакции пополнения"""
        db_obj = TransactionDB(
            user_id=user_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            description=description or "Пополнение баланса"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_withdrawal(
        self, db: Session, *, user_id: str, amount: float, 
        description: str = "", task_id: Optional[str] = None
    ) -> TransactionDB:
        """Создание транзакции списания"""
        db_obj = TransactionDB(
            user_id=user_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            description=description or "Списание средств",
            task_id=task_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_transaction = CRUDTransaction(TransactionDB)
