import sqlite3
import os
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def migrate_database():
    """Міграція бази даних для додавання нового поля subscription_type до таблиці user"""
    
    db_path = 'instance/content_generator.db'
    
    # Перевірка, чи існує база даних
    if not os.path.exists(db_path):
        logger.error(f"База даних {db_path} не знайдена")
        return False
    
    try:
        # Підключення до бази даних
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Перевірка, чи існує колонка subscription_type
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'subscription_type' not in column_names:
            logger.info("Додавання колонки subscription_type до таблиці user")
            cursor.execute("ALTER TABLE user ADD COLUMN subscription_type TEXT DEFAULT 'none'")
            conn.commit()
            logger.info("Колонку subscription_type успішно додано")
        else:
            logger.info("Колонка subscription_type вже існує")
        
        # Закриття з'єднання
        conn.close()
        
        logger.info("Міграцію бази даних успішно завершено")
        return True
    
    except Exception as e:
        logger.error(f"Помилка при міграції бази даних: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_database() 