import pytest
import requests
from typing import Generator

BASE_URL = "http://localhost/api/v1"


@pytest.fixture(scope="session")
def base_url() -> str:
    """Базовый URL API"""
    return BASE_URL


@pytest.fixture(scope="session")
def test_user() -> dict:
    """Тестовые данные пользователя"""
    return {
        "username": "pytest_user",
        "email": "pytest@example.com",
        "password": "Test123!@#"
    }


@pytest.fixture(scope="session")
def registered_user(base_url: str, test_user: dict) -> Generator[dict, None, None]:
    """Зарегистрированный пользователь"""
    # Регистрация
    response = requests.post(
        f"{base_url}/auth/register",
        json=test_user
    )
    assert response.status_code == 200
    user_data = response.json()

    yield user_data

    # Очистка после тестов (опционально)
    # Можно добавить удаление пользователя через админку


@pytest.fixture(scope="session")
def user_token(base_url: str, test_user: dict) -> str:
    """Токен авторизации"""
    response = requests.post(
        f"{base_url}/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(user_token: str) -> dict:
    """Заголовки с авторизацией"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(scope="session")
def test_model_id(base_url: str, auth_headers: dict) -> str:
    """ID тестовой модели"""
    response = requests.get(
        f"{base_url}/models/",
        headers=auth_headers
    )
    assert response.status_code == 200
    models = response.json()
    assert len(models) > 0
    return models[0]["id"]