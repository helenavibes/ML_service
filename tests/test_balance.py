import pytest
import requests


class TestBalance:
    """Тестирование работы с балансом"""

    def test_get_balance_initial(self, base_url, auth_headers):
        """Получение начального баланса"""
        response = requests.get(
            f"{base_url}/balance/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "balance" in data
        assert "user_id" in data
        assert "username" in data
        assert data["balance"] == 0.0

    def test_deposit_success(self, base_url, auth_headers):
        """Успешное пополнение баланса"""
        deposit_amount = 100.0

        response = requests.post(
            f"{base_url}/balance/deposit",
            headers=auth_headers,
            json={"amount": deposit_amount}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["amount"] == deposit_amount
        assert data["new_balance"] == deposit_amount
        assert "transaction_id" in data
        assert data["description"] == "Пополнение баланса"

    def test_deposit_negative_amount(self, base_url, auth_headers):
        """Ошибка при пополнении на отрицательную сумму"""
        response = requests.post(
            f"{base_url}/balance/deposit",
            headers=auth_headers,
            json={"amount": -50.0}
        )
        # FastAPI возвращает 422 для ошибок валидации
        assert response.status_code == 422

    def test_deposit_zero_amount(self, base_url, auth_headers):
        """Ошибка при пополнении на ноль"""
        response = requests.post(
            f"{base_url}/balance/deposit",
            headers=auth_headers,
            json={"amount": 0}
        )
        assert response.status_code == 422

    def test_balance_update_after_deposit(self, base_url, auth_headers):
        """Проверка обновления баланса после пополнения"""
        # Получаем текущий баланс
        initial = requests.get(
            f"{base_url}/balance/",
            headers=auth_headers
        ).json()["balance"]

        # Пополняем
        deposit = 50.0
        requests.post(
            f"{base_url}/balance/deposit",
            headers=auth_headers,
            json={"amount": deposit}
        )

        # Проверяем новый баланс
        final = requests.get(
            f"{base_url}/balance/",
            headers=auth_headers
        ).json()["balance"]

        assert final == initial + deposit