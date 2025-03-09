#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
import getpass

# URL для запиту (локальний сервер Flask)
BASE_URL = "http://127.0.0.1:5001"

def test_scraper(niche, token=None):
    """
    Тестування ендпоінту скрейпера
    
    Args:
        niche (str): Ніша для пошуку хештегів
        token (str, optional): JWT токен для авторизації
    """
    # Якщо токен не передано, спробуємо спочатку авторизуватися
    if not token:
        print("Токен не передано. Спробуємо авторизуватися...")
        
        # Запитуємо дані для авторизації
        email = input("Введіть email: ")
        password = getpass.getpass("Введіть пароль: ")
        
        # Дані для авторизації
        login_data = {
            "email": email,
            "password": password
        }
        
        # Спроба авторизації
        try:
            login_response = requests.post(f"{BASE_URL}/login", json=login_data)
            login_response.raise_for_status()
            
            # Отримання токена
            token = login_response.json().get("token")
            if not token:
                print("Помилка: Не вдалося отримати токен авторизації")
                return
                
            print(f"Успішна авторизація. Отримано токен: {token[:20]}...")
            
        except requests.RequestException as e:
            print(f"Помилка при авторизації: {str(e)}")
            return
    
    # Заголовки для запиту
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Дані для запиту
    data = {
        "niche": niche,
        "count": 5
    }
    
    # Виконання запиту до ендпоінту скрейпера
    try:
        print(f"Відправляємо запит на скрейпінг хештегів для ніші '{niche}'...")
        response = requests.post(f"{BASE_URL}/scrape", headers=headers, json=data)
        
        # Перевірка статусу відповіді
        if response.status_code == 200:
            result = response.json()
            print("\nУспішно отримано хештеги:")
            print(f"Ніша: {result.get('niche')}")
            print(f"Хештеги: {', '.join(result.get('hashtags', []))}")
            
            # Перевірка, чи створено файл hashtags.json
            print("\nПеревірка файлу hashtags.json...")
            try:
                with open("hashtags.json", "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    print(f"Файл hashtags.json створено успішно:")
                    print(f"Ніша: {file_data.get('niche')}")
                    print(f"Хештеги: {', '.join(file_data.get('hashtags', []))}")
                    print(f"Час створення: {file_data.get('timestamp')}")
            except FileNotFoundError:
                print("Файл hashtags.json не знайдено")
            except json.JSONDecodeError:
                print("Помилка при читанні файлу hashtags.json: невалідний JSON")
            
        else:
            print(f"Помилка при скрейпінгу: {response.status_code}")
            print(f"Відповідь: {response.text}")
            
    except requests.RequestException as e:
        print(f"Помилка при виконанні запиту: {str(e)}")

if __name__ == "__main__":
    # Отримання ніші з аргументів командного рядка або використання значення за замовчуванням
    niche = sys.argv[1] if len(sys.argv) > 1 else "подорожі"
    
    # Виклик функції тестування
    test_scraper(niche) 