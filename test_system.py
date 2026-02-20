#!/usr/bin/env python3
"""
Системное тестирование ML Service Platform
Проверка всех критических сценариев работы
"""

import requests
import time
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000/api/v1"
WEB_URL = "http://localhost:8000"

class MLServiceTester:
    """Класс для тестирования системы"""
    
    def __init__(self):
        self.token = None
        self.user_id = None
        self.test_user = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "Test123!@#"
        }
        self.models = []
        self.task_ids = []
        
    def print_header(self, text):
        """Печать заголовка"""
        print("\n" + "="*60)
        print(f" {text}")
        print("="*60)
    
    def print_result(self, name, status, details=""):
        """Печать результата теста"""
        icon = "✅" if status else "❌"
        print(f" {icon} {name}: {details}")
        return status
    
    def test_health(self):
        """Проверка здоровья сервиса"""
        try:
            response = requests.get(f"{WEB_URL}/health")
            return self.print_result(
                "Health check", 
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            return self.print_result("Health check", False, str(e))
    
    def test_registration(self):
        """Тест регистрации нового пользователя"""
        self.print_header("1. ТЕСТИРОВАНИЕ РЕГИСТРАЦИИ")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=self.test_user
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data["id"]
                return self.print_result(
                    "Регистрация", 
                    True,
                    f"Пользователь {self.test_user['username']} создан, ID: {self.user_id[:8]}..."
                )
            else:
                return self.print_result(
                    "Регистрация", 
                    False,
                    f"Ошибка {response.status_code}: {response.text}"
                )
        except Exception as e:
            return self.print_result("Регистрация", False, str(e))
    
    def test_login(self):
        """Тест авторизации"""
        self.print_header("2. ТЕСТИРОВАНИЕ АВТОРИЗАЦИИ")
        
        try:
            # Правильные данные
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": self.test_user["username"],
                    "password": self.test_user["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.print_result(
                    "Авторизация (верные данные)", 
                    True,
                    "Токен получен"
                )
            else:
                self.print_result(
                    "Авторизация (верные данные)", 
                    False,
                    f"Ошибка {response.status_code}"
                )
                return False
            
            # Неправильный пароль
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": self.test_user["username"],
                    "password": "wrong_password"
                }
            )
            
            self.print_result(
                "Авторизация (неверный пароль)", 
                response.status_code == 401,
                f"Ожидается 401, получено {response.status_code}"
            )
            
            return True
            
        except Exception as e:
            return self.print_result("Авторизация", False, str(e))
    
    def test_get_balance(self):
        """Тест получения баланса"""
        self.print_header("3. ТЕСТИРОВАНИЕ БАЛАНСА")
        
        try:
            response = requests.get(
                f"{BASE_URL}/balance/",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.initial_balance = data["balance"]
                return self.print_result(
                    "Получение баланса", 
                    True,
                    f"Начальный баланс: {data['balance']} кредитов"
                )
            else:
                return self.print_result(
                    "Получение баланса", 
                    False,
                    f"Ошибка {response.status_code}"
                )
        except Exception as e:
            return self.print_result("Получение баланса", False, str(e))
    
    def test_deposit(self):
        """Тест пополнения баланса"""
        
        deposit_amount = 100
        response = requests.post(
            f"{BASE_URL}/balance/deposit",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"amount": deposit_amount}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Проверяем новый баланс
            balance_response = requests.get(
                f"{BASE_URL}/balance/",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            new_balance = balance_response.json()["balance"]
            
            expected = self.initial_balance + deposit_amount
            is_correct = (new_balance == expected)
            
            return self.print_result(
                "Пополнение баланса", 
                is_correct,
                f"Было: {self.initial_balance}, +{deposit_amount} = {new_balance} (ожидалось {expected})"
            )
        else:
            return self.print_result(
                "Пополнение баланса", 
                False,
                f"Ошибка {response.status_code}"
            )
    
    def test_get_models(self):
        """Тест получения списка моделей"""
        self.print_header("4. ТЕСТИРОВАНИЕ ML МОДЕЛЕЙ")
        
        try:
            response = requests.get(
                f"{BASE_URL}/models/",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                self.models = response.json()
                return self.print_result(
                    "Получение списка моделей", 
                    True,
                    f"Найдено {len(self.models)} моделей"
                )
            else:
                return self.print_result(
                    "Получение списка моделей", 
                    False,
                    f"Ошибка {response.status_code}"
                )
        except Exception as e:
            return self.print_result("Получение списка моделей", False, str(e))
    
    def test_prediction_success(self):
        """Тест успешного предсказания"""
        self.print_header("5. ТЕСТИРОВАНИЕ ПРЕДСКАЗАНИЙ")
        
        if not self.models:
            return self.print_result("Предсказание", False, "Нет доступных моделей")
        
        model = self.models[0]
        
        # Получаем текущий баланс
        balance_before = requests.get(
            f"{BASE_URL}/balance/",
            headers={"Authorization": f"Bearer {self.token}"}
        ).json()["balance"]
        
        # Отправляем корректные данные
        response = requests.post(
            f"{BASE_URL}/tasks/",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "model_id": model["id"],
                "features": {"x1": 2.5, "x2": 3.7}
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data["task_id"]
            self.task_ids.append(task_id)
            
            # Проверяем списание (ждем немного)
            time.sleep(2)
            
            balance_after = requests.get(
                f"{BASE_URL}/balance/",
                headers={"Authorization": f"Bearer {self.token}"}
            ).json()["balance"]
            
            cost = model.get("cost_per_prediction", 1.0)
            expected_balance = balance_before - cost
            
            is_spent = (balance_after == expected_balance)
            
            self.print_result(
                "Создание задачи", 
                True,
                f"Task ID: {task_id[:8]}..., стоимость: {cost}"
            )
            
            self.print_result(
                "Списание средств", 
                is_spent,
                f"Было: {balance_before}, стало: {balance_after}, ожидалось: {expected_balance}"
            )
            
            # Проверяем статус задачи
            time.sleep(1)
            status_response = requests.get(
                f"{BASE_URL}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                self.print_result(
                    "Статус задачи", 
                    status_data["status"] in ["PENDING", "PROCESSING", "COMPLETED"],
                    f"Статус: {status_data['status']}"
                )
            
            return True
        else:
            return self.print_result(
                "Предсказание", 
                False,
                f"Ошибка {response.status_code}: {response.text}"
            )
    
    def test_prediction_insufficient_balance(self):
        """Тест предсказания при недостаточном балансе"""
        
        # Сначала потратим все кредиты (если есть)
        balance = requests.get(
            f"{BASE_URL}/balance/",
            headers={"Authorization": f"Bearer {self.token}"}
        ).json()["balance"]
        
        if balance > 0:
            # Отправляем запросы пока не кончатся кредиты
            model = self.models[0]
            cost = model.get("cost_per_prediction", 1.0)
            
            requests_to_make = int(balance / cost) + 1
            
            for i in range(requests_to_make):
                response = requests.post(
                    f"{BASE_URL}/tasks/",
                    headers={"Authorization": f"Bearer {self.token}"},
                    json={
                        "model_id": model["id"],
                        "features": {"x1": 1.0, "x2": 2.0}
                    }
                )
                
                if i == requests_to_make - 1:
                    # Последний запрос должен вернуть ошибку
                    return self.print_result(
                        "Предсказание (недостаточно средств)", 
                        response.status_code in [400, 402, 403],
                        f"Статус: {response.status_code}, ожидается ошибка"
                    )
        
        return self.print_result(
            "Предсказание (недостаточно средств)", 
            True,
            "Пропущено (баланс уже 0)"
        )
    
    def test_prediction_invalid_data(self):
        """Тест предсказания с некорректными данными"""
        
        if not self.models:
            return self.print_result("Некорректные данные", False, "Нет моделей")
        
        model = self.models[0]
        
        # Отправляем данные без обязательных полей
        response = requests.post(
            f"{BASE_URL}/tasks/",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "model_id": model["id"],
                "features": {"wrong_field": 123}
            }
        )
        
        # Должна быть ошибка валидации (400 или 422)
        is_error = response.status_code in [400, 422]
        
        return self.print_result(
            "Валидация данных (некорректные)", 
            is_error,
            f"Статус: {response.status_code}, {'✅ ошибка' if is_error else '❌ должно быть ошибкой'}"
        )
    
    def test_history(self):
        """Тест истории операций"""
        self.print_header("6. ТЕСТИРОВАНИЕ ИСТОРИИ")
        
        try:
            # История транзакций
            tx_response = requests.get(
                f"{BASE_URL}/history/transactions",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if tx_response.status_code == 200:
                tx_data = tx_response.json()
                self.print_result(
                    "История транзакций", 
                    True,
                    f"Найдено {len(tx_data)} транзакций"
                )
            else:
                self.print_result(
                    "История транзакций", 
                    False,
                    f"Ошибка {tx_response.status_code}"
                )
            
            # История предсказаний
            pred_response = requests.get(
                f"{BASE_URL}/history/predictions",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if pred_response.status_code == 200:
                pred_data = pred_response.json()
                self.print_result(
                    "История предсказаний", 
                    True,
                    f"Найдено {len(pred_data)} предсказаний"
                )
            else:
                self.print_result(
                    "История предсказаний", 
                    False,
                    f"Ошибка {pred_response.status_code}"
                )
            
            return True
            
        except Exception as e:
            return self.print_result("История", False, str(e))
    
    def test_web_interface(self):
        """Проверка доступности веб-интерфейса"""
        self.print_header("7. ТЕСТИРОВАНИЕ WEB ИНТЕРФЕЙСА")
        
        pages = [
            ("Главная", "/"),
            ("Вход", "/auth/login"),
            ("Регистрация", "/auth/register"),
        ]
        
        all_ok = True
        for name, path in pages:
            try:
                response = requests.get(f"{WEB_URL}{path}")
                is_ok = response.status_code == 200
                self.print_result(
                    f"Страница {name}", 
                    is_ok,
                    f"{path} - {response.status_code}"
                )
                if not is_ok:
                    all_ok = False
            except Exception as e:
                self.print_result(f"Страница {name}", False, str(e))
                all_ok = False
        
        return all_ok
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        self.print_header("🚀 СИСТЕМНОЕ ТЕСТИРОВАНИЕ ML SERVICE PLATFORM")
        print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Тестовый пользователь: {self.test_user['username']}")
        
        tests = [
            ("Health check", self.test_health),
            ("Регистрация", self.test_registration),
            ("Авторизация", self.test_login),
            ("Получение баланса", self.test_get_balance),
            ("Пополнение баланса", self.test_deposit),
            ("Список моделей", self.test_get_models),
            ("Успешное предсказание", self.test_prediction_success),
            ("Некорректные данные", self.test_prediction_invalid_data),
            ("Недостаточно средств", self.test_prediction_insufficient_balance),
            ("История операций", self.test_history),
            ("Web интерфейс", self.test_web_interface),
        ]
        
        results = []
        for name, test_func in tests:
            print(f"\n▶️  {name}")
            result = test_func()
            results.append(result)
            time.sleep(1)
        
        self.print_header("📊 ИТОГИ ТЕСТИРОВАНИЯ")
        passed = sum(1 for r in results if r)
        total = len(results)
        
        print(f"\n   Пройдено тестов: {passed}/{total}")
        
        if passed == total:
            print("\n   🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("   Система работает корректно")
        else:
            print(f"\n   ⚠️  Провалено тестов: {total - passed}")
            print("   Требуется доработка")
        
        print(f"\nВремя завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return passed == total

def main():
    """Основная функция"""
    tester = MLServiceTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
