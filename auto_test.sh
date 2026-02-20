#!/bin/bash

echo "🔄 Автоматическое тестирование ML сервиса"
echo "========================================="

# Функция для получения нового токена
get_token() {
    echo "🔑 Получаем новый токен..."
    TOKEN=$(curl -s -X POST "http://localhost/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=testuser&password=pass123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

    if [ -n "$TOKEN" ]; then
        echo "✅ Токен получен: ${TOKEN:0:20}..."
        export TOKEN
        return 0
    else
        echo "❌ Ошибка получения токена"
        return 1
    fi
}

# Функция для проверки баланса
check_balance() {
    echo -e "\n💰 Проверка баланса..."
    curl -s -X GET "http://localhost/api/v1/balance/" \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
}

# Функция для отправки предсказания
send_prediction() {
    local data="$1"
    echo -e "\n📤 Отправка предсказания с данными: $data"

    # Отправляем запрос и сохраняем ответ
    RESPONSE=$(curl -s -X POST "http://localhost/api/v1/predict/" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$data")

    # Пробуем распарсить JSON
    if echo "$RESPONSE" | python3 -m json.tool 2>/dev/null; then
        # Если JSON валидный, проверяем на ошибки аутентификации
        if echo "$RESPONSE" | grep -q "Could not validate credentials"; then
            echo "⚠️ Токен истек, обновляем..."
            get_token
            if [ $? -eq 0 ]; then
                echo "🔄 Повторная отправка с новым токеном..."
                curl -s -X POST "http://localhost/api/v1/predict/" \
                    -H "Authorization: Bearer $TOKEN" \
                    -H "Content-Type: application/json" \
                    -d "$data" | python3 -m json.tool
            fi
        fi
    else
        echo "❌ Ошибка: ответ не в формате JSON"
        echo "Сырой ответ: $RESPONSE"
    fi
}

# Функция для проверки истории
check_history() {
    echo -e "\n📋 Проверка истории предсказаний..."
    curl -s -X GET "http://localhost/api/v1/history/predictions" \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
}

# Главная функция
main() {
    # Получаем начальный токен
    get_token
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Проверяем начальный баланс
    check_balance
    
    # Тест 1: Одно предсказание
    echo -e "\n📌 ТЕСТ 1: Одно предсказание"
    send_prediction '{
        "model_id": "bea79793-8433-4cab-9587-d5ea64e8e5b3",
        "data": [{"x1": 2.5, "x2": 3.7}]
    }'
    sleep 2

    # Тест 2: Несколько предсказаний
    echo -e "\n📌 ТЕСТ 2: Несколько предсказаний"
    send_prediction '{
        "model_id": "bea79793-8433-4cab-9587-d5ea64e8e5b3",
        "data": [
            {"x1": 1.0, "x2": 2.0},
            {"x1": 3.0, "x2": 4.0},
            {"x1": 5.0, "x2": 6.0}
        ]
    }'
    sleep 2
    
    # Проверяем финальный баланс
    check_balance
    
    # Проверяем историю
    check_history
    
    echo -e "\n✅ Тестирование завершено!"
}

# Запускаем главную функцию
main