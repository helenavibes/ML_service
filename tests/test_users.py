import pytest
import requests
import time


class TestUsers:
    """Тестирование работы с пользователями"""

    def test_register_success(self, base_url, test_user):
        """Успешная регистрация нового пользователя"""
        # Пытаемся зарегистрировать пользователя с уникальным именем
        unique_user = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "Test123!@#"
        }

        response = requests.post(
            f"{base_url}/auth/register",
            json=unique_user
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == unique_user["username"]
        assert data["email"] == unique_user["email"]
        assert data["role"] == "USER"

    def test_register_duplicate_username(self, base_url, test_user):
        """Ошибка при регистрации с существующим username"""
        # Пытаемся зарегистрировать того же пользователя
        response = requests.post(
            f"{base_url}/auth/register",
            json=test_user
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower()

    def test_register_invalid_email(self, base_url):
        """Ошибка при невалидном email"""
        invalid_user = {
            "username": "invalid_user",
            "email": "not-an-email",
            "password": "password123"
        }

        response = requests.post(
            f"{base_url}/auth/register",
            json=invalid_user
        )

        assert response.status_code == 422  # Validation Error

    def test_login_success(self, base_url, test_user):
        """Успешная авторизация"""
        response = requests.post(
            f"{base_url}/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800

        # Токен должен быть строкой и не пустым
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, base_url, test_user):
        """Ошибка при неверном пароле"""
        response = requests.post(
            f"{base_url}/auth/login",
            data={
                "username": test_user["username"],
                "password": "wrong_password"
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_nonexistent_user(self, base_url):
        """Ошибка при входе несуществующего пользователя"""
        response = requests.post(
            f"{base_url}/auth/login",
            data={
                "username": "i_dont_exist",
                "password": "password123"
            }
        )

        assert response.status_code == 401

    def test_get_current_user(self, base_url, auth_headers, test_user):
        """Получение информации о текущем пользователе"""
        response = requests.get(
            f"{base_url}/auth/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]
        assert data["role"] == "USER"

    def test_get_current_user_unauthorized(self, base_url):
        """Ошибка при запросе без токена"""
        response = requests.get(f"{base_url}/auth/me")
        assert response.status_code == 401