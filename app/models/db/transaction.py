from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.models.db.base import Base
from app.models.enums import TransactionType

class TransactionDB(Base):
    """Модель транзакции для базы данных"""
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text)
    task_id = Column(String(36), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    user = relationship("UserDB", backref="transactions")
    
    def __repr__(self):
        return f"<TransactionDB(id={self.id}, type={self.transaction_type}, amount={self.amount})>"
