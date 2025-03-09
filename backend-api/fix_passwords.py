#!/usr/bin/env python3
"""
Скрипт для виправлення паролів у базі даних.
Цей скрипт оновлює всі паролі користувачів, які не мають правильного формату хешу.
"""

from app import db, User, app
from werkzeug.security import generate_password_hash, check_password_hash
import sys

def fix_passwords():
    """Виправляє паролі користувачів у базі даних."""
    with app.app_context():
        users = User.query.all()
        fixed_count = 0
        
        print(f"Знайдено {len(users)} користувачів у базі даних.")
        
        for user in users:
            print(f"Перевірка користувача: {user.email}")
            
            # Перевіряємо, чи пароль має правильний формат хешу
            try:
                # Спроба розпарсити хеш (якщо це можливо)
                if ':' not in user.password:
                    # Пароль не має правильного формату
                    print(f"  - Пароль користувача {user.email} не має правильного формату хешу.")
                    
                    # Встановлюємо тимчасовий пароль "password123"
                    new_password = "password123"
                    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
                    
                    user.password = hashed_password
                    fixed_count += 1
                    print(f"  - Пароль оновлено на тимчасовий: 'password123'")
            except Exception as e:
                print(f"  - Помилка при перевірці пароля: {e}")
                
                # Встановлюємо тимчасовий пароль "password123"
                new_password = "password123"
                hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
                
                user.password = hashed_password
                fixed_count += 1
                print(f"  - Пароль оновлено на тимчасовий: 'password123'")
        
        if fixed_count > 0:
            db.session.commit()
            print(f"\nУспішно оновлено {fixed_count} паролів.")
        else:
            print("\nУсі паролі мають правильний формат.")

if __name__ == "__main__":
    print("Запуск скрипта для виправлення паролів...")
    fix_passwords()
    print("Скрипт завершено.") 