#!/usr/bin/env python3

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Завантаження змінних середовища
load_dotenv()

# Отримання API ключа
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key (перші 10 символів): {api_key[:10]}...")

# Ініціалізація клієнта
client = OpenAI(api_key=api_key)

# Тестовий промпт
system_message = "Ти - експертний генератор ідей для контенту. Відповідай у форматі JSON."
user_message = "Згенеруй 5 ідей для YouTube-відео в ніші подорожі для молоді. Для кожної ідеї надай заголовок, хук та опис. Відповідай у форматі JSON."

try:
    print("Відправляю запит до OpenAI API...")
    
    # Виклик OpenAI API
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    # Отримання та парсинг відповіді
    response_content = response.choices[0].message.content
    print("\nВідповідь від API:")
    print(response_content)
    
    # Парсинг JSON
    response_json = json.loads(response_content)
    print("\nУспішно розпарсили JSON!")
    
    # Виведення ідей
    if "ideas" in response_json:
        ideas = response_json["ideas"]
    else:
        # Шукаємо масив в корені відповіді
        for key, value in response_json.items():
            if isinstance(value, list) and len(value) > 0:
                ideas = value
                break
        else:
            ideas = []
    
    print(f"\nОтримано {len(ideas)} ідей:")
    for i, idea in enumerate(ideas, 1):
        print(f"\nІдея {i}:")
        print(f"Заголовок: {idea.get('title', 'Не вказано')}")
        print(f"Хук: {idea.get('hook', 'Не вказано')}")
        print(f"Опис: {idea.get('description', 'Не вказано')}")
    
    print("\nТест успішно завершено!")
    
except Exception as e:
    print(f"\nПомилка при тестуванні API: {str(e)}") 