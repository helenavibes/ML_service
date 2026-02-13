from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import uuid
from app.models.db.base import Base
from app.models.enums import UserRole

class UserDB(Base):
    """Модель пользователя для базы данных"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)  # ✅ Используем Enum
    balance = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<UserDB(id={self.id}, username={self.username}, role={self.role})>"
