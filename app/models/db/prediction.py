from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.models.db.base import Base
from app.models.enums import TaskStatus

class PredictionTaskDB(Base):
    """Модель задачи предсказания для базы данных"""
    __tablename__ = "prediction_tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id = Column(String(36), ForeignKey("ml_models.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    input_data = Column(JSON, nullable=False)
    valid_data = Column(JSON)
    invalid_data = Column(JSON)
    result = Column(JSON)
    total_cost = Column(Float)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    
    user = relationship("UserDB", backref="prediction_tasks")
    model = relationship("MLModelDB", backref="prediction_tasks")
    
    def __repr__(self):
        return f"<PredictionTaskDB(id={self.id}, status={self.status})>"
