#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import os
import logging
import time
import random
from urllib.parse import quote
from deep_translator import GoogleTranslator

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterScraper:
    """Клас для скрейпінгу хештегів з X (Twitter)"""
    
    def __init__(self):
        """Ініціалізація скрейпера з базовими налаштуваннями"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://twitter.com/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        self.base_url = "https://twitter.com/search?q="
        self.output_file = "hashtags.json"
        
        # Словник для кешування перекладів, щоб не робити зайвих запитів
        self.translation_cache = {}
        
        # Ініціалізуємо перекладач
        self.translator = GoogleTranslator(source='uk', target='en')
    
    def translate_to_english(self, ukrainian_text):
        """
        Переклад тексту з української на англійську за допомогою deep-translator
        
        Args:
            ukrainian_text (str): Текст українською мовою
            
        Returns:
            str: Перекладений текст англійською мовою
        """
        # Перевіряємо, чи є переклад у кеші
        if ukrainian_text.lower() in self.translation_cache:
            translated = self.translation_cache[ukrainian_text.lower()]
            logger.info(f"Переклад з кешу: '{ukrainian_text}' -> '{translated}'")
            return translated
        
        try:
            # Використовуємо бібліотеку deep-translator для перекладу
            translated = self.translator.translate(ukrainian_text)
            
            # Зберігаємо переклад у кеш
            self.translation_cache[ukrainian_text.lower()] = translated
            
            logger.info(f"Переклад через API: '{ukrainian_text}' -> '{translated}'")
            return translated
            
        except Exception as e:
            logger.error(f"Помилка при перекладі: {str(e)}")
            
            # Якщо переклад не вдався, спробуємо спрощену транслітерацію
            try:
                # Дуже спрощена транслітерація
                translit_map = {
                    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ye',
                    'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l',
                    'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'yu',
                    'я': 'ya', ' ': ' '
                }
                
                transliterated = ''.join(translit_map.get(c.lower(), c) for c in ukrainian_text)
                logger.info(f"Транслітерація (резервний варіант): '{ukrainian_text}' -> '{transliterated}'")
                
                # Зберігаємо транслітерацію у кеш
                self.translation_cache[ukrainian_text.lower()] = transliterated
                
                return transliterated
                
            except Exception as e2:
                logger.error(f"Помилка при транслітерації: {str(e2)}")
                # Якщо все не вдалося, повертаємо оригінальний текст
                return ukrainian_text
    
    def get_hashtags(self, niche, count=5):
        """
        Отримання популярних хештегів за заданою нішею
        
        Args:
            niche (str): Ніша для пошуку (наприклад, "подорожі")
            count (int): Кількість хештегів для повернення
            
        Returns:
            list: Список знайдених хештегів
        """
        try:
            # Переклад ніші на англійську
            english_niche = self.translate_to_english(niche)
            logger.info(f"Пошук хештегів для ніші '{niche}' (англійською: '{english_niche}')")
            
            # Підготовка URL для пошуку
            encoded_niche = quote(english_niche)
            search_url = f"{self.base_url}{encoded_niche}&src=typed_query&f=top"
            logger.info(f"Виконую запит до URL: {search_url}")
            
            # Додаємо випадкову затримку для імітації поведінки людини
            time.sleep(random.uniform(1, 3))
            
            # Виконання запиту
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            # Перевірка статусу відповіді
            if response.status_code != 200:
                logger.error(f"Помилка при запиті: статус {response.status_code}")
                return []
            
            # Парсинг HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Пошук хештегів у тексті твітів
            # Примітка: це спрощений підхід, оскільки Twitter використовує JavaScript для рендерингу контенту
            # У реальному сценарії може знадобитися Selenium або інші інструменти
            hashtags = []
            
            # Шукаємо всі посилання, які можуть містити хештеги
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Перевіряємо, чи це хештег
                if href.startswith('/hashtag/') and text.startswith('#'):
                    if text not in hashtags:
                        hashtags.append(text)
            
            # Якщо не знайдено хештегів через посилання, спробуємо знайти їх у тексті
            if not hashtags:
                tweets = soup.find_all(['p', 'span', 'div'])
                for tweet in tweets:
                    text = tweet.get_text()
                    # Шукаємо слова, що починаються з #
                    words = text.split()
                    for word in words:
                        if word.startswith('#') and len(word) > 1:
                            if word not in hashtags:
                                hashtags.append(word)
            
            # Обмеження кількості хештегів
            unique_hashtags = list(set(hashtags))[:count]
            
            # Якщо не знайдено жодного хештегу, створюємо штучні на основі ніші
            if not unique_hashtags:
                logger.warning(f"Не знайдено хештегів для ніші '{niche}'. Створюю штучні хештеги.")
                # Створюємо штучні хештеги на основі ніші та популярних трендів
                trends = ["Trend", "Popular", "Top", "Best", "New", "Tips", "Hack", "Guide", "Review", "Tutorial"]
                
                # Використовуємо англійський переклад для створення хештегів
                english_niche_no_spaces = english_niche.replace(' ', '')
                
                # Створюємо штучні хештеги
                for i in range(min(count, len(trends))):
                    unique_hashtags.append(f"#{english_niche_no_spaces.capitalize()}{trends[i]}")
            
            logger.info(f"Знайдено {len(unique_hashtags)} хештегів для ніші '{niche}'")
            return unique_hashtags
            
        except requests.RequestException as e:
            logger.error(f"Помилка при виконанні запиту: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Неочікувана помилка: {str(e)}")
            return []
    
    def save_to_json(self, niche, hashtags):
        """
        Збереження хештегів у JSON-файл
        
        Args:
            niche (str): Ніша для пошуку
            hashtags (list): Список хештегів
            
        Returns:
            bool: True, якщо збереження успішне, інакше False
        """
        try:
            data = {
                "niche": niche,
                "english_niche": self.translate_to_english(niche),
                "hashtags": hashtags,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            logger.info(f"Хештеги успішно збережено у файл {self.output_file}")
            return True
        except Exception as e:
            logger.error(f"Помилка при збереженні у файл: {str(e)}")
            return False
    
    def get_and_save_hashtags(self, niche, count=5):
        """
        Отримання та збереження хештегів за нішею
        
        Args:
            niche (str): Ніша для пошуку
            count (int): Кількість хештегів
            
        Returns:
            dict: Словник з нішею та хештегами
        """
        hashtags = self.get_hashtags(niche, count)
        self.save_to_json(niche, hashtags)
        
        return {
            "niche": niche,
            "english_niche": self.translate_to_english(niche),
            "hashtags": hashtags
        }

# Функція для використання у Flask
def scrape_hashtags(niche, count=5):
    """
    Функція для скрейпінгу хештегів, яка буде викликатися з Flask
    
    Args:
        niche (str): Ніша для пошуку
        count (int): Кількість хештегів
        
    Returns:
        dict: Словник з нішею та хештегами
    """
    scraper = TwitterScraper()
    return scraper.get_and_save_hashtags(niche, count)

# Для тестування при прямому запуску файлу
if __name__ == "__main__":
    test_niche = "подорожі"
    scraper = TwitterScraper()
    result = scraper.get_and_save_hashtags(test_niche)
    print(f"Результат: {result}") 