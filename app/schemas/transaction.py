from typing import Optional
from pydantic import BaseModel
from app.models.enums import TransactionType
from datetime import datetime

class TransactionResponse(BaseModel):
    id: str
    transaction_type: TransactionType
    amount: float
    description: Optional[str] = None
    task_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionHistoryResponse(BaseModel):
    transactions: list[TransactionResponse]
    total_count: int
    page: int
    per_page: int
