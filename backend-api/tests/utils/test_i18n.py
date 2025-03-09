"""
Тести для функцій локалізації.
"""

import pytest
import os
import sys
import json
import tempfile

# Додаємо кореневу директорію проєкту до шляху імпорту
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.i18n import load_translations

@pytest.fixture
def temp_locales_dir():
    """Створює тимчасову директорію для файлів локалізації."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Створюємо файли локалізації
        uk_translations = {
            "messages": {
                "success": "Успіх",
                "error": "Помилка"
            },
            "auth": {
                "login_success": "Успішний вхід",
                "login_failed": "Невдалий вхід"
            }
        }
        
        en_translations = {
            "messages": {
                "success": "Success",
                "error": "Error"
            },
            "auth": {
                "login_success": "Login successful",
                "login_failed": "Login failed"
            }
        }
        
        # Створюємо директорію locales
        locales_dir = os.path.join(temp_dir, "locales")
        os.makedirs(locales_dir, exist_ok=True)
        
        # Записуємо файли локалізації
        with open(os.path.join(locales_dir, "uk.json"), "w", encoding="utf-8") as f:
            json.dump(uk_translations, f, ensure_ascii=False, indent=2)
        
        with open(os.path.join(locales_dir, "en.json"), "w", encoding="utf-8") as f:
            json.dump(en_translations, f, ensure_ascii=False, indent=2)
        
        yield temp_dir

def test_load_translations(temp_locales_dir, monkeypatch):
    """Тестує функцію load_translations."""
    # Мокаємо шлях до файлів локалізації
    def mock_dirname(path):
        return temp_locales_dir
    
    monkeypatch.setattr(os.path, "dirname", mock_dirname)
    
    # Тестуємо завантаження українських перекладів
    uk_translations = load_translations("uk")
    assert uk_translations is not None
    assert "messages" in uk_translations
    assert "auth" in uk_translations
    assert uk_translations["messages"]["success"] == "Успіх"
    assert uk_translations["auth"]["login_success"] == "Успішний вхід"
    
    # Тестуємо завантаження англійських перекладів
    en_translations = load_translations("en")
    assert en_translations is not None
    assert "messages" in en_translations
    assert "auth" in en_translations
    assert en_translations["messages"]["success"] == "Success"
    assert en_translations["auth"]["login_success"] == "Login successful"

def test_load_translations_default_locale(temp_locales_dir, monkeypatch):
    """Тестує функцію load_translations з локаллю за замовчуванням."""
    # Мокаємо шлях до файлів локалізації
    def mock_dirname(path):
        return temp_locales_dir
    
    monkeypatch.setattr(os.path, "dirname", mock_dirname)
    
    # Тестуємо завантаження перекладів без вказання локалі
    translations = load_translations()
    assert translations is not None
    assert "messages" in translations
    assert "auth" in translations
    assert translations["messages"]["success"] == "Успіх"  # Українська за замовчуванням

def test_load_translations_unsupported_locale(temp_locales_dir, monkeypatch):
    """Тестує функцію load_translations з непідтримуваною локаллю."""
    # Мокаємо шлях до файлів локалізації
    def mock_dirname(path):
        return temp_locales_dir
    
    monkeypatch.setattr(os.path, "dirname", mock_dirname)
    
    # Тестуємо завантаження перекладів з непідтримуваною локаллю
    translations = load_translations("fr")  # Французька не підтримується
    assert translations is not None
    assert "messages" in translations
    assert "auth" in translations
    assert translations["messages"]["success"] == "Успіх"  # Українська за замовчуванням

def test_load_translations_file_not_found(temp_locales_dir, monkeypatch):
    """Тестує функцію load_translations, коли файл не знайдено."""
    # Мокаємо шлях до файлів локалізації
    def mock_dirname(path):
        return os.path.join(temp_locales_dir, "nonexistent")  # Неіснуюча директорія
    
    monkeypatch.setattr(os.path, "dirname", mock_dirname)
    
    # Тестуємо завантаження перекладів, коли файл не знайдено
    translations = load_translations("uk")
    assert translations == {} 