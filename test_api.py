#!/usr/bin/env python3
"""
Тестирование API эндпоинтов
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "ML Service Platform"
    print("✅ Root endpoint works")

def test_health():
    """Тест health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health endpoint works")

def test_registration():
    """Тест регистрации пользователя"""
    # Уникальный username чтобы не конфликтовать
    import random
    username = f"testuser_{random.randint(1000, 9999)}"
    
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "test123",
            "role": "USER"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    assert data["email"] == f"{username}@example.com"
    assert data["balance"] == 0.0
    print(f"✅ Registration works for user: {username}")
    return data

def test_login():
    """Тест авторизации"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "demo_user",
            "password": "demo123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    print("✅ Login works for demo_user")
    return data["access_token"]

def test_get_models(token):
    """Тест получения списка моделей"""
    response = client.get(
        "/api/v1/models/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    models = response.json()
    assert len(models) >= 2
    print(f"✅ Get models works, found {len(models)} models")
    return models

def test_get_balance(token):
    """Тест получения баланса"""
    response = client.get(
        "/api/v1/balance/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "balance" in data
    print(f"✅ Get balance works: {data['balance']}")
    return data

def test_deposit(token):
    """Тест пополнения баланса"""
    response = client.post(
        "/api/v1/balance/deposit",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": 50.0,
            "description": "Test deposit"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 50.0
    assert data["new_balance"] > 0
    print(f"✅ Deposit works: new balance = {data['new_balance']}")

def test_create_prediction(token, models):
    """Тест создания предсказания"""
    if not models:
        print("⚠️ No models available, skipping prediction test")
        return
    
    model_id = models[0]["id"]
    response = client.post(
        "/api/v1/predict/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "model_id": model_id,
            "data": [
                {"feature1": 1.0, "feature2": 2.0},
                {"feature1": 3.0, "feature2": 4.0}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == model_id
    assert "task_id" in data
    print(f"✅ Create prediction works: task_id = {data['task_id']}")
    return data["task_id"]

def test_get_prediction(token, task_id):
    """Тест получения предсказания"""
    if not task_id:
        print("⚠️ No task_id, skipping get prediction test")
        return
    
    response = client.get(
        f"/api/v1/predict/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    print(f"✅ Get prediction works: status = {data['status']}")

def test_get_prediction_history(token):
    """Тест получения истории предсказаний"""
    response = client.get(
        "/api/v1/history/predictions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Get prediction history works: {len(data)} items")

def test_get_transaction_history(token):
    """Тест получения истории транзакций"""
    response = client.get(
        "/api/v1/history/transactions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Get transaction history works: {len(data)} items")

def main():
    """Основная функция тестирования"""
    print("=" * 50)
    print("🚀 ТЕСТИРОВАНИЕ API")
    print("=" * 50)
    
    # Базовые тесты
    test_root()
    test_health()
    
    # Тесты с авторизацией
    token = test_login()
    models = test_get_models(token)
    balance = test_get_balance(token)
    test_deposit(token)
    task_id = test_create_prediction(token, models)
    if task_id:
        test_get_prediction(token, task_id)
    test_get_prediction_history(token)
    test_get_transaction_history(token)
    
    print("\n" + "=" * 50)
    print("🎉 ВСЕ ТЕСТЫ API ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 50)

if __name__ == "__main__":
    main()
