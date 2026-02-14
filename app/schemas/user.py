from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.enums import UserRole
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[UserRole] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    id: str
    username: str
    email: str
    role: UserRole
    balance: float
    is_active: bool
    created_at: datetime
    
    @classmethod
    def from_orm(cls, obj):
        """Преобразование из ORM объекта"""
        return cls(
            id=str(obj.id),
            username=obj.username,
            email=obj.email,
            role=obj.role,
            balance=float(obj.balance),
            is_active=obj.is_active,
            created_at=obj.created_at
        )

class UserAdminResponse(UserResponse):
    password_hash: Optional[str] = None
    updated_at: datetime
