#!/usr/bin/env python3

import os
import sys
import sqlite3
import datetime
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Шлях до бази даних
DB_PATH = 'instance/content_generator.db'

def activate_subscription(email):
    """Активує підписку для користувача за його email"""
    
    # Перевірка, чи існує файл бази даних
    if not os.path.exists(DB_PATH):
        print(f"Помилка: Файл бази даних {DB_PATH} не знайдено.")
        return False
    
    try:
        # Підключення до бази даних
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Пошук користувача за email
        cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Помилка: Користувача з email {email} не знайдено.")
            return False
        
        # Встановлення підписки
        subscription_end = datetime.datetime.now() + datetime.timedelta(days=30)
        cursor.execute(
            "UPDATE user SET is_subscribed = ?, subscription_end = ? WHERE email = ?",
            (True, subscription_end, email)
        )
        
        # Збереження змін
        conn.commit()
        
        print(f"Підписку для користувача {email} успішно активовано до {subscription_end}.")
        return True
    
    except sqlite3.Error as e:
        print(f"Помилка SQLite: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Використання: python activate_subscription.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    success = activate_subscription(email)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1) 