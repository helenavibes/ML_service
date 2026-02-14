from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class BalanceResponse(BaseModel):
    balance: float
    user_id: str
    username: str

class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма пополнения (больше 0)")
    description: Optional[str] = "Пополнение баланса"

class DepositResponse(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    new_balance: float
    description: str
    created_at: datetime
