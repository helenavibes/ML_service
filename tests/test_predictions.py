import pytest
import requests
import time  # Добавьте этот импорт

class TestPredictions:
    """Тестирование ML предсказаний"""

    def test_prediction_success(self, base_url, auth_headers, test_model_id):
        """Успешное создание задачи на предсказание"""
        payload = {
            "model_id": test_model_id,
            "data": [{"x1": 2.5, "x2": 3.7}]
        }

        response = requests.post(
            f"{base_url}/predict/",
            headers=auth_headers,
            json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert "task_id" in data
        assert data["status"] == "PENDING"
        assert data["model_id"] == test_model_id
        assert data["valid_data_count"] == 1
        assert data["invalid_data_count"] == 0
        assert data["cost"] > 0

    def test_prediction_multiple_items(self, base_url, auth_headers, test_model_id):
        """Предсказание с несколькими записями"""
        payload = {
            "model_id": test_model_id,
            "data": [
                {"x1": 1.0, "x2": 2.0},
                {"x1": 3.0, "x2": 4.0},
                {"x1": 5.0, "x2": 6.0}
            ]
        }

        response = requests.post(
            f"{base_url}/predict/",
            headers=auth_headers,
            json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert data["valid_data_count"] == 3
        assert data["cost"] > 0

    def test_prediction_missing_fields(self, base_url, auth_headers, test_model_id):
        """Ошибка при отсутствии обязательных полей"""
        payload = {
            "model_id": test_model_id,
            "data": [{"wrong": "data"}]
        }

        response = requests.post(
            f"{base_url}/predict/",
            headers=auth_headers,
            json=payload
        )

        assert response.status_code == 400

    def test_prediction_invalid_model(self, base_url, auth_headers):
        """Ошибка при несуществующей модели"""
        payload = {
            "model_id": "00000000-0000-0000-0000-000000000000",
            "data": [{"x1": 1.0, "x2": 2.0}]
        }

        response = requests.post(
            f"{base_url}/predict/",
            headers=auth_headers,
            json=payload
        )

        assert response.status_code == 404

    def test_prediction_insufficient_balance(self, base_url, test_model_id):
        """Ошибка при недостаточном балансе (отдельный пользователь)"""
        # 1. Создаем уникального пользователя с нулевым балансом
        unique_username = f"lowbalance_{int(time.time())}"
        unique_email = f"{unique_username}@example.com"

        reg_response = requests.post(
            f"{base_url}/auth/register",
            json={
                "username": unique_username,
                "email": unique_email,
                "password": "Test123!@#"
            }
        )
        assert reg_response.status_code == 200

        # 2. Логинимся и получаем токен
        login_response = requests.post(
            f"{base_url}/auth/login",
            data={"username": unique_username, "password": "Test123!@#"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Проверяем, что баланс действительно 0
        balance_response = requests.get(f"{base_url}/balance/", headers=headers)
        assert balance_response.json()["balance"] == 0.0

        # 4. Пытаемся сделать предсказание
        payload = {
            "model_id": test_model_id,
            "data": [{"x1": 1.0, "x2": 2.0}]
        }
        response = requests.post(
            f"{base_url}/predict/",
            headers=headers,
            json=payload
        )

        # 5. Проверяем, что получили ошибку 400
        assert response.status_code == 400
        assert "insufficient balance" in response.text.lower()

    def test_prediction_without_auth(self, base_url, test_model_id):
        """Ошибка при запросе без авторизации"""
        payload = {
            "model_id": test_model_id,
            "data": [{"x1": 1.0, "x2": 2.0}]
        }

        response = requests.post(
            f"{base_url}/predict/",
            json=payload
        )

        assert response.status_code == 401