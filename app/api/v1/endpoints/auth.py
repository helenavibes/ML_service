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
    try:
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
        
        # Преобразуем UUID в строку для ответа
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "balance": float(user.balance),
            "is_active": user.is_active,
            "created_at": user.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", response_model=TokenResponse)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Авторизация пользователя (получение JWT токена)
    """
    try:
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
        
        # Создание токена
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt.encode(
            {
                "sub": user.username,
                "user_id": str(user.id),
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user = Depends(deps.get_current_active_user)
) -> Any:
    """
    Получение информации о текущем пользователе
    """
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "balance": float(current_user.balance),
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }
