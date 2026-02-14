from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
import uuid
from app.models.db.base import Base
from app.models.enums import ModelType

class MLModelDB(Base):
    """Модель ML модели для базы данных"""
    __tablename__ = "ml_models"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    model_type = Column(Enum(ModelType), nullable=False)
    cost_per_prediction = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def calculate_cost(self, data_count: int) -> float:
        """Рассчитать стоимость предсказания для N записей"""
        return self.cost_per_prediction * data_count
    
    def __repr__(self):
        return f"<MLModelDB(id={self.id}, name={self.name}, cost={self.cost_per_prediction})>"
