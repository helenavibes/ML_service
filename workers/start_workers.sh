#!/bin/bash

echo "🚀 Запуск ML воркеров..."
echo "================================"

# Количество воркеров
WORKERS=3

# Переходим в папку с воркерами
cd "$(dirname "$0")"

# Активируем виртуальное окружение из корня проекта
source ../.venv/bin/activate

# Запускаем воркеры
for i in $(seq 1 $WORKERS); do
    echo "Запуск worker-$i..."
    python worker.py --id "worker-$i" &
    sleep 1
done

echo ""
echo "✅ Все $WORKERS воркеров запущены"
echo "Для остановки нажмите Ctrl+C"

# Ждем сигнала остановки
wait
