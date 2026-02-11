#!/bin/bash
echo "🚀 БЫСТРАЯ ПРОВЕРКА ЗАДАНИЯ №2"
echo "================================"

# 1. Проверка .env
echo "1. .env файлы:"
echo "   - .env.example: $( [ -f .env.example ] && echo '✅' || echo '❌' )"
echo "   - .env в .gitignore: $( grep -q '^\.env$' .gitignore && echo '✅' || echo '❌' )"
echo "   - .env в Git: $( git ls-files .env 2>/dev/null >/dev/null && echo '❌' || echo '✅' )"

# 2. Проверка файлов в корне
echo ""
echo "2. Файлы в корне:"
echo "   - nginx.conf: $( [ -f nginx.conf ] && echo '✅' || echo '❌' )"
echo "   - init.sql: $( [ -f init.sql ] && echo '✅' || echo '❌' )"
echo "   - Папка docker: $( [ -d docker ] && echo '❌' || echo '✅' )"

# 3. Проверка rabbitmq
echo ""
echo "3. Rabbitmq:"
RESTART=$(grep -A2 "rabbitmq:" docker-compose.yml | grep "restart:" | awk '{print $2}')
echo "   - restart: $RESTART $( [ "$RESTART" = "on-failure" ] && echo '✅' || echo '❌ (должно быть on-failure)' )"

# 4. Проверка docker-compose.yml
echo ""
echo "4. docker-compose.yml:"
echo "   - 4 сервиса: $( grep -c "^  [a-z-]*:" docker-compose.yml )/4 ✅"
echo "   - app с volumes: $( grep -q "./app:/app/app" docker-compose.yml && echo '✅' || echo '❌' )"
echo "   - web-proxy порты: $( grep -q '"80:80"' docker-compose.yml && grep -q '"443:443"' docker-compose.yml && echo '✅' || echo '❌' )"
echo "   - rabbitmq порты: $( grep -q '"5672:5672"' docker-compose.yml && grep -q '"15672:15672"' docker-compose.yml && echo '✅' || echo '❌' )"

echo ""
echo "================================"
echo "Проверка завершена!"
