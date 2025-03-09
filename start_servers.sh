#!/bin/bash

# Кольори для виводу
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== ContentAI - Запуск серверів ===${NC}"

# Зупинка всіх попередніх процесів
echo -e "${YELLOW}Зупинка попередніх процесів...${NC}"
pkill -f "python3 app.py" || true
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Перевірка, чи всі процеси зупинені
if lsof -ti:5001 >/dev/null 2>&1; then
    echo -e "${RED}Помилка: Порт 5001 все ще зайнятий. Спробуйте перезапустити термінал.${NC}"
    exit 1
fi

if lsof -ti:3000 >/dev/null 2>&1; then
    echo -e "${RED}Помилка: Порт 3000 все ще зайнятий. Спробуйте перезапустити термінал.${NC}"
    exit 1
fi

# Запуск бекенд-сервера
echo -e "${YELLOW}Запуск бекенд-сервера...${NC}"
cd /Users/stanislavpolusin/contentAI/backend-api
source venv/bin/activate
python3 app.py > backend.log 2>&1 &
BACKEND_PID=$!

# Перевірка, чи запустився бекенд-сервер
sleep 3
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}Помилка: Бекенд-сервер не запустився. Перевірте логи в backend.log${NC}"
    cat backend.log | tail -n 20
    exit 1
fi

# Перевірка, чи відповідає бекенд-сервер на запити
sleep 2
if ! curl -s http://127.0.0.1:5001/health > /dev/null; then
    echo -e "${RED}Помилка: Бекенд-сервер не відповідає на запити. Перевірте логи в backend.log${NC}"
    cat backend.log | tail -n 20
    exit 1
fi

echo -e "${GREEN}Бекенд-сервер успішно запущено на порту 5001${NC}"

# Запуск фронтенд-сервера
echo -e "${YELLOW}Запуск фронтенд-сервера...${NC}"
cd /Users/stanislavpolusin/contentAI/frontend-app
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Перевірка, чи запустився фронтенд-сервер
sleep 5
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${RED}Помилка: Фронтенд-сервер не запустився. Перевірте логи в frontend.log${NC}"
    cat frontend.log | tail -n 20
    exit 1
fi

echo -e "${GREEN}Фронтенд-сервер успішно запущено на порту 3000${NC}"

# Виведення інформації про запущені сервери
echo -e "${GREEN}=== Сервери успішно запущено ===${NC}"
echo -e "${GREEN}Бекенд: http://127.0.0.1:5001${NC}"
echo -e "${GREEN}Фронтенд: http://localhost:3000${NC}"
echo -e "${YELLOW}Логи бекенду: backend.log${NC}"
echo -e "${YELLOW}Логи фронтенду: frontend.log${NC}"
echo -e "${YELLOW}Для зупинки серверів виконайте: pkill -f 'python3 app.py' && pkill -f 'next'${NC}" 