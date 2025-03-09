#!/bin/bash

# Активація віртуального середовища
source venv/bin/activate

# Запуск Flask-сервера на порту 5001 (порт 5000 може бути зайнятий AirTunes на macOS)
python3 app.py 