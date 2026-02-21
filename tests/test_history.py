import pytest
import requests
from datetime import datetime


class TestHistory:
    """Тестирование истории операций"""

    def test_prediction_history_empty(self, base_url, auth_headers):
        """Пустая история предсказаний для нового пользователя"""
        response = requests.get(
            f"{base_url}/history/predictions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_prediction_history_after_creation(self, base_url, auth_headers, test_model_id):
        """История предсказаний после создания задачи"""
        # Создаем предсказание
        payload = {
            "model_id": test_model_id,
            "data": [{"x1": 1.0, "x2": 2.0}]
        }
        predict_response = requests.post(
            f"{base_url}/predict/",
            headers=auth_headers,
            json=payload
        )
        assert predict_response.status_code == 200
        task_id = predict_response.json()["task_id"]

        # Проверяем историю
        history_response = requests.get(
            f"{base_url}/history/predictions",
            headers=auth_headers
        )

        assert history_response.status_code == 200
        history = history_response.json()

        # Ищем нашу задачу
        found = False
        for item in history:
            if item["id"] == task_id:
                found = True
                assert item["model_id"] == test_model_id
                assert item["model_name"] is not None
                assert item["status"] in ["PENDING", "COMPLETED"]
                assert item["valid_data_count"] == 1
                assert "created_at" in item
                break

        assert found, f"Task {task_id} not found in history"

    def test_transaction_history(self, base_url, auth_headers):
        """История транзакций"""
        response = requests.get(
            f"{base_url}/history/transactions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Проверяем структуру транзакции если есть записи
        if data:
            tx = data[0]
            assert "id" in tx
            assert "transaction_type" in tx
            assert "amount" in tx
            assert "created_at" in tx

    def test_history_pagination(self, base_url, auth_headers):
        """Проверка пагинации истории"""
        response = requests.get(
            f"{base_url}/history/predictions?skip=0&limit=5",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_history_unauthorized(self, base_url):
        """Ошибка при запросе истории без авторизации"""
        response = requests.get(f"{base_url}/history/predictions")
        assert response.status_code == 401