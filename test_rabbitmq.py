#!/usr/bin/env python3
"""
Тестирование RabbitMQ интеграции
"""

import requests
import time
import json
from pprint import pprint

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Проверка здоровья API"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ API работает")

def test_login():
    """Авторизация"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "demo_user", "password": "demo123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    print("✅ Авторизация успешна")
    return token

def test_create_async_task(token):
    """Создание асинхронной задачи"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Данные для предсказания
    task_data = {
        "model_id": "ea76e379-114b-405b-8eb1-0037e5084d78",  # Text Classifier
        "features": {
            "x1": 1.5,
            "x2": 2.7
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks/",
        headers=headers,
        json=task_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Задача создана: {data['task_id']}, статус: {data['status']}")
        return data['task_id']
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")
        return None

def test_check_status(token, task_id):
    """Проверка статуса задачи"""
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(5):
        time.sleep(1)
        response = requests.get(
            f"{BASE_URL}/tasks/{task_id}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Статус через {i+1}с: {data['status']}")
            if data['status'] != "PENDING":
                break

def test_models(token):
    """Получение списка моделей"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/models/", headers=headers)
    if response.status_code == 200:
        models = response.json()
        print(f"✅ Найдено моделей: {len(models)}")
        for m in models:
            print(f"  - {m['name']}: {m['id']}")
        return models
    return None

def main():
    print("=" * 50)
    print("🚀 ТЕСТИРОВАНИЕ RABBITMQ ИНТЕГРАЦИИ")
    print("=" * 50)
    
    # Проверка API
    test_health()
    
    # Авторизация
    token = test_login()
    if not token:
        return
    
    # Получение моделей
    models = test_models(token)
    if not models:
        return
    
    # Создаем несколько задач
    print("\n📤 Отправка 5 задач...")
    task_ids = []
    for i in range(5):
        task_id = test_create_async_task(token)
        if task_id:
            task_ids.append(task_id)
        time.sleep(0.2)
    
    # Проверяем статусы
    print("\n📊 Проверка статусов...")
    for task_id in task_ids:
        test_check_status(token, task_id)
    
    print("\n✅ Тестирование завершено!")
    print("Проверьте логи воркеров для подтверждения обработки.")

if __name__ == "__main__":
    main()
