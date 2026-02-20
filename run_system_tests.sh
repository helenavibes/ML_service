#!/bin/bash

echo "========================================="
echo "🚀 ЗАПУСК СИСТЕМНОГО ТЕСТИРОВАНИЯ"
echo "========================================="

# Проверяем что сервер запущен
echo "🔍 Проверка доступности сервера..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Сервер доступен"
else
    echo "❌ Сервер не доступен! Запустите сервер: uvicorn app.main:app --reload"
    exit 1
fi

# Проверяем что Docker контейнеры запущены
echo "🔍 Проверка Docker контейнеров..."
if docker ps | grep -q rabbitmq; then
    echo "✅ RabbitMQ запущен"
else
    echo "⚠️ RabbitMQ не запущен, запускаем..."
    docker-compose up -d rabbitmq
fi

if docker ps | grep -q postgres; then
    echo "✅ PostgreSQL запущен"
else
    echo "⚠️ PostgreSQL не запущен, запускаем..."
    docker-compose up -d database
fi

if docker ps | grep -q worker; then
    echo "✅ Воркеры запущены"
else
    echo "⚠️ Воркеры не запущены, запускаем..."
    docker-compose up -d worker
fi

echo ""
echo "========================================="
echo "📋 ЗАПУСК ТЕСТОВ"
echo "========================================="

# Запускаем тесты
python test_system.py

# Сохраняем результат
RESULT=$?

echo ""
echo "========================================="
if [ $RESULT -eq 0 ]; then
    echo "🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!"
else
    echo "❌ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ"
fi
echo "========================================="

exit $RESULT
