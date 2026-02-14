from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.db.user import UserDB
from pydantic import BaseModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    # balance не нужен при создании, будет 0.0 по умолчанию

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    balance: Optional[float] = None
    is_active: Optional[bool] = None

class CRUDUser(CRUDBase[UserDB, UserCreate, UserUpdate]):
    
    def get_by_username(self, db: Session, username: str) -> Optional[UserDB]:
        return db.query(UserDB).filter(UserDB.username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[UserDB]:
        return db.query(UserDB).filter(UserDB.email == email).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> UserDB:
        hashed_password = pwd_context.hash(obj_in.password)
        db_obj = UserDB(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=hashed_password,
            balance=0.0,  # Явно указываем начальный баланс
            is_active=True,
            role='USER'  # Добавляем роль по умолчанию
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[UserDB]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not pwd_context.verify(password, user.password_hash):
            return None
        return user
    
    def update_balance(self, db: Session, user_id: str, amount: float) -> Optional[UserDB]:
        user = self.get(db, user_id)
        if user:
            user.balance += amount
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

crud_user = CRUDUser(UserDB)
