import requests
import json

print("🔍 Тестирование баланса...")

# Логин
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "debug_test", "password": "debug123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Токен получен: {token[:20]}...")
    
    # Получение баланса (правильный URL)
    balance_response = requests.get(
        "http://localhost:8000/api/v1/balance/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Баланс URL: /api/v1/balance/")
    print(f"Status: {balance_response.status_code}")
    print(f"Response: {balance_response.json()}")
else:
    print("❌ Ошибка логина")
