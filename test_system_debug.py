#!/usr/bin/env python3
"""
Диагностическое тестирование
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def debug_request(url, method="GET", **kwargs):
    """Выполнить запрос и вывести детали"""
    print(f"\n--- {method} {url} ---")
    try:
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        else:
            response = None
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text[:200]}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_registration():
    """Тест регистрации с деталями"""
    test_user = {
        "username": "debug_test",
        "email": "debug@test.com",
        "password": "debug123"
    }
    
    print("\n=== ТЕСТ РЕГИСТРАЦИИ ===")
    response = debug_request(
        f"{BASE_URL}/auth/register",
        method="POST",
        json=test_user
    )
    return response

def test_login():
    """Тест логина с деталями"""
    print("\n=== ТЕСТ ЛОГИНА ===")
    response = debug_request(
        f"{BASE_URL}/auth/login",
        method="POST",
        data={"username": "debug_test", "password": "debug123"}
    )
    return response

def test_balance(user_id):
    """Тест баланса"""
    print("\n=== ТЕСТ БАЛАНСА ===")
    response = debug_request(f"{BASE_URL}/balance/{user_id}")
    return response

if __name__ == "__main__":
    reg_response = test_registration()
    if reg_response and reg_response.status_code == 200:
        user_id = reg_response.json().get("id")
        test_login()
        if user_id:
            test_balance(user_id)
