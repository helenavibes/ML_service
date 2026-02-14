from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.crud.user import crud_user
from app.database.database import get_db
from app.schemas.user import UserCreate, UserResponse, TokenResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Регистрация нового пользователя
    """
    # Проверка уникальности username
    user = crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Проверка уникальности email
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Создание пользователя
    user = crud_user.create(db, obj_in=user_in)
    return user

@router.post("/login", response_model=TokenResponse)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Авторизация пользователя (получение JWT токена)
    """
    # Аутентификация
    user = crud_user.authenticate(
        db, 
        username=form_data.username, 
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверка активности
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Создание токена - преобразуем UUID в строку!
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {
            "sub": user.username,
            "user_id": str(user.id),  # ✅ Преобразуем UUID в строку!
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "exp": datetime.utcnow() + access_token_expires
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user = Depends(deps.get_current_active_user)
) -> Any:
    """
    Получение информации о текущем пользователе
    """
    return current_user
