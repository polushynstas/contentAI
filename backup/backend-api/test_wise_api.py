import requests
import os
from dotenv import load_dotenv
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Завантаження змінних середовища
load_dotenv()
wise_api_key = os.getenv("WISE_API_KEY")

if not wise_api_key:
    logger.error("WISE_API_KEY не знайдено в .env файлі")
    exit(1)

logger.info(f"WISE_API_KEY знайдено (перші 10 символів): {wise_api_key[:10]}...")

# Використовуємо продакшн URL
base_url = "https://api.transferwise.com"
# base_url = "https://api.sandbox.transferwise.tech"  # Для тестового середовища

# Тест 1: Отримання профілів
def test_get_profiles():
    logger.info("Тест 1: Отримання профілів")
    
    url = f"{base_url}/v1/profiles"
    headers = {
        "Authorization": f"Bearer {wise_api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            profiles = response.json()
            logger.info(f"Успішно отримано профілі. Кількість: {len(profiles)}")
            for profile in profiles:
                logger.info(f"Профіль ID: {profile.get('id')}, Тип: {profile.get('type')}, Повне ім'я: {profile.get('fullName')}")
            return profiles
        else:
            logger.error(f"Помилка при отриманні профілів. Код відповіді: {response.status_code}")
            logger.error(f"Відповідь: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Виникла помилка: {str(e)}")
        return None

# Тест 2: Отримання балансів (якщо є профіль)
def test_get_balances(profile_id):
    logger.info(f"Тест 2: Отримання балансів для профілю {profile_id}")
    
    url = f"{base_url}/v1/borderless-accounts?profileId={profile_id}"
    headers = {
        "Authorization": f"Bearer {wise_api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            accounts = response.json()
            logger.info(f"Успішно отримано рахунки. Кількість: {len(accounts)}")
            for account in accounts:
                logger.info(f"Рахунок ID: {account.get('id')}")
                balances = account.get('balances', [])
                for balance in balances:
                    logger.info(f"Валюта: {balance.get('currency')}, Баланс: {balance.get('amount')}")
            return accounts
        else:
            logger.error(f"Помилка при отриманні балансів. Код відповіді: {response.status_code}")
            logger.error(f"Відповідь: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Виникла помилка: {str(e)}")
        return None

# Запуск тестів
if __name__ == "__main__":
    logger.info("Початок тестування Wise API")
    
    profiles = test_get_profiles()
    
    if profiles and len(profiles) > 0:
        profile_id = profiles[0].get('id')
        test_get_balances(profile_id)
    
    logger.info("Завершення тестування Wise API") 