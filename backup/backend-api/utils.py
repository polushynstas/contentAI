import json
import os

def load_translations(locale='uk'):
    """
    Завантажує переклади для вказаної локалі.
    
    Args:
        locale (str): Код локалі (uk або en)
        
    Returns:
        dict: Словник з перекладами
    """
    # Перевіряємо, чи підтримується локаль
    if locale not in ['uk', 'en']:
        locale = 'uk'  # Використовуємо українську мову за замовчуванням
    
    # Шлях до файлу перекладів
    translations_file = os.path.join(os.path.dirname(__file__), 'locales', f'{locale}.json')
    
    try:
        with open(translations_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        return translations
    except Exception as e:
        print(f"Помилка при завантаженні перекладів: {str(e)}")
        # Повертаємо порожній словник у випадку помилки
        return {} 