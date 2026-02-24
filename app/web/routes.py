from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.api import deps
from app.database.database import get_db
from app.models.db.user import UserDB
from app.crud.user import crud_user
from app.crud.transaction import crud_transaction
from app.crud.prediction import crud_prediction
from app.crud.ml_model import crud_ml_model
from app.schemas.user import UserCreate, UserLogin
import httpx
import os

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

# API клиент для внутренних запросов
API_URL = "http://localhost:8000/api/v1"

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница"""
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "user": request.cookies.get("user")
        }
    )

@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )

@router.post("/auth/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Обработка входа"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/auth/login",
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            redirect = RedirectResponse(url="/dashboard", status_code=302)
            redirect.set_cookie(key="access_token", value=token_data["access_token"])
            redirect.set_cookie(key="user", value=username)
            return redirect
        else:
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Неверное имя пользователя или пароль"
                },
                status_code=401
            )

@router.get("/auth/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )

@router.post("/auth/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """Обработка регистрации"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        
        if response.status_code == 200:
            return RedirectResponse(url="/auth/login", status_code=302)
        else:
            error_detail = response.json().get("detail", "Ошибка регистрации")
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "error": error_detail
                },
                status_code=400
            )

@router.get("/auth/logout")
async def logout():
    """Выход из системы"""
    redirect = RedirectResponse(url="/", status_code=302)
    redirect.delete_cookie("access_token")
    redirect.delete_cookie("user")
    return redirect

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Личный кабинет"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    async with httpx.AsyncClient() as client:
        # Получаем информацию о пользователе
        user_response = await client.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if user_response.status_code != 200:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        user_data = user_response.json()
        
        # Получаем баланс
        balance_response = await client.get(
            f"{API_URL}/balance/",
            headers={"Authorization": f"Bearer {token}"}
        )
        balance_data = balance_response.json() if balance_response.status_code == 200 else {"balance": 0}
        
        # Получаем последние предсказания
        history_response = await client.get(
            f"{API_URL}/history/predictions?limit=5",
            headers={"Authorization": f"Bearer {token}"}
        )
        predictions = history_response.json() if history_response.status_code == 200 else []
    
    return templates.TemplateResponse(
        "dashboard/profile.html",
        {
            "request": request,
            "user": user_data,
            "balance": balance_data.get("balance", 0),
            "predictions": predictions
        }
    )

@router.get("/balance", response_class=HTMLResponse)
async def balance_page(request: Request):
    """Страница управления балансом"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    async with httpx.AsyncClient() as client:
        # Получаем информацию о пользователе
        user_response = await client.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if user_response.status_code != 200:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        user_data = user_response.json()
        
        # Получаем баланс
        balance_response = await client.get(
            f"{API_URL}/balance/",
            headers={"Authorization": f"Bearer {token}"}
        )
        balance_data = balance_response.json() if balance_response.status_code == 200 else {"balance": 0}
        
        # Получаем историю транзакций
        transactions_response = await client.get(
            f"{API_URL}/history/transactions?limit=10",
            headers={"Authorization": f"Bearer {token}"}
        )
        transactions = transactions_response.json() if transactions_response.status_code == 200 else []
    
    return templates.TemplateResponse(
        "dashboard/balance.html",
        {
            "request": request,
            "user": user_data,
            "balance": balance_data.get("balance", 0),
            "transactions": transactions
        }
    )

@router.post("/balance/deposit")
async def deposit(
    request: Request,
    amount: float = Form(...)
):
    """Пополнение баланса"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/balance/deposit",
            headers={"Authorization": f"Bearer {token}"},
            json={"amount": amount}
        )
        
        if response.status_code == 200:
            return RedirectResponse(url="/balance", status_code=302)
        else:
            error_detail = response.json().get("detail", "Ошибка пополнения")
            return templates.TemplateResponse(
                "dashboard/balance.html",
                {
                    "request": request,
                    "error": error_detail
                },
                status_code=400
            )

@router.get("/predict", response_class=HTMLResponse)
async def predict_page(request: Request):
    """Страница предсказания"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    async with httpx.AsyncClient() as client:
        # Получаем информацию о пользователе
        user_response = await client.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if user_response.status_code != 200:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        user_data = user_response.json()
        
        # Получаем баланс
        balance_response = await client.get(
            f"{API_URL}/balance/",
            headers={"Authorization": f"Bearer {token}"}
        )
        balance_data = balance_response.json() if balance_response.status_code == 200 else {"balance": 0}
        
        # Получаем список моделей
        models_response = await client.get(
            f"{API_URL}/models/",
            headers={"Authorization": f"Bearer {token}"}
        )
        models = models_response.json() if models_response.status_code == 200 else []
    
    return templates.TemplateResponse(
        "ml/predict.html",
        {
            "request": request,
            "user": user_data,
            "balance": balance_data.get("balance", 0),
            "models": models
        }
    )

@router.post("/predict")
async def predict(
    request: Request,
    model_id: str = Form(...),
    x1: float = Form(...),
    x2: float = Form(...)
):
    """Отправка задачи на предсказание"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    features = {"x1": x1, "x2": x2}
    
    async with httpx.AsyncClient() as client:
        # Проверяем баланс
        balance_response = await client.get(
            f"{API_URL}/balance/",
            headers={"Authorization": f"Bearer {token}"}
        )
        balance_data = balance_response.json() if balance_response.status_code == 200 else {"balance": 0}
        
        # Отправляем задачу
        response = await client.post(
            f"{API_URL}/tasks/",
            headers={"Authorization": f"Bearer {token}"},
            json={"model_id": model_id, "features": features}
        )
        
        if response.status_code == 200:
            result = response.json()
            return templates.TemplateResponse(
                "ml/result.html",
                {
                    "request": request,
                    "task_id": result["task_id"],
                    "status": result["status"],
                    "created_at": result["created_at"]
                }
            )
        else:
            error_detail = response.json().get("detail", "Ошибка выполнения")
            return templates.TemplateResponse(
                "ml/predict.html",
                {
                    "request": request,
                    "error": error_detail,
                    "balance": balance_data.get("balance", 0)
                },
                status_code=400
            )

@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Страница истории"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    async with httpx.AsyncClient() as client:
        # Получаем информацию о пользователе
        user_response = await client.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if user_response.status_code != 200:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        user_data = user_response.json()
        
        # Получаем историю предсказаний
        predictions_response = await client.get(
            f"{API_URL}/history/predictions",
            headers={"Authorization": f"Bearer {token}"}
        )
        predictions = predictions_response.json() if predictions_response.status_code == 200 else []
        
        # Получаем историю транзакций
        transactions_response = await client.get(
            f"{API_URL}/history/transactions",
            headers={"Authorization": f"Bearer {token}"}
        )
        transactions = transactions_response.json() if transactions_response.status_code == 200 else []
    
    return templates.TemplateResponse(
        "dashboard/history.html",
        {
            "request": request,
            "user": user_data,
            "predictions": predictions,
            "transactions": transactions
        }
    )

@router.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    """Страница со списком моделей"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    async with httpx.AsyncClient() as client:
        # Получаем информацию о пользователе
        user_response = await client.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if user_response.status_code != 200:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        user_data = user_response.json()
        
        # Получаем список моделей
        models_response = await client.get(
            f"{API_URL}/models/",
            headers={"Authorization": f"Bearer {token}"}
        )
        models = models_response.json() if models_response.status_code == 200 else []
    
    return templates.TemplateResponse(
        "ml/models.html",
        {
            "request": request,
            "user": user_data,
            "models": models
        }
    )
