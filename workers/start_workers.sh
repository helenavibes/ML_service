#!/bin/bash

echo "🚀 Запуск ML воркеров..."
echo "================================"

# Количество воркеров
WORKERS=3

# Активируем виртуальное окружение
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
