#!/bin/bash

# Кольори для виводу
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== ContentAI - Зупинка серверів ===${NC}"

# Зупинка бекенд-сервера
echo -e "${YELLOW}Зупинка бекенд-сервера...${NC}"
if pgrep -f "python3 app.py" > /dev/null; then
    pkill -f "python3 app.py"
    echo -e "${GREEN}Бекенд-сервер зупинено${NC}"
else
    echo -e "${YELLOW}Бекенд-сервер не запущено${NC}"
fi

# Зупинка фронтенд-сервера
echo -e "${YELLOW}Зупинка фронтенд-сервера...${NC}"
if pgrep -f "next" > /dev/null; then
    pkill -f "next"
    echo -e "${GREEN}Фронтенд-сервер зупинено${NC}"
else
    echo -e "${YELLOW}Фронтенд-сервер не запущено${NC}"
fi

# Перевірка, чи всі процеси зупинені
if lsof -ti:5001 > /dev/null 2>&1; then
    echo -e "${RED}Увага: Порт 5001 все ще зайнятий. Спробуйте виконати: lsof -ti:5001 | xargs kill -9${NC}"
else
    echo -e "${GREEN}Порт 5001 вільний${NC}"
fi

if lsof -ti:3000 > /dev/null 2>&1; then
    echo -e "${RED}Увага: Порт 3000 все ще зайнятий. Спробуйте виконати: lsof -ti:3000 | xargs kill -9${NC}"
else
    echo -e "${GREEN}Порт 3000 вільний${NC}"
fi

echo -e "${GREEN}=== Сервери зупинено ===${NC}" 