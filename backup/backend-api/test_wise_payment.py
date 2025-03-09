import requests
import os
import uuid
import time
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

# Використовуємо тестове середовище (sandbox)
base_url = "https://api.sandbox.transferwise.tech"
# base_url = "https://api.transferwise.com"  # Для продакшн середовища

# Бізнес-профіль
profile_id = 66654409

# Тест 1: Створення котирування (quote)
def test_create_quote(amount=1.00, currency="USD"):
    logger.info(f"Тест 1: Створення котирування для суми {amount} {currency}")
    
    quote_url = f"{base_url}/v2/quotes"
    headers = {
        "Authorization": f"Bearer {wise_api_key}",
        "Content-Type": "application/json"
    }
    
    quote_payload = {
        "profileId": profile_id,
        "sourceCurrency": currency,
        "targetCurrency": currency,
        "sourceAmount": amount,
        "preferredPayIn": "BALANCE"
    }
    
    try:
        response = requests.post(quote_url, headers=headers, json=quote_payload)
        
        if response.status_code == 200:
            quote = response.json()
            logger.info(f"Котирування успішно створено з ID: {quote.get('id')}")
            return quote
        else:
            logger.error(f"Помилка при створенні котирування. Код відповіді: {response.status_code}")
            logger.error(f"Відповідь: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Виникла помилка: {str(e)}")
        return None

# Тест 2: Пошук або створення одержувача (recipient)
def test_find_or_create_recipient(currency="USD"):
    logger.info(f"Тест 2: Пошук або створення одержувача для валюти {currency}")
    
    headers = {
        "Authorization": f"Bearer {wise_api_key}",
        "Content-Type": "application/json"
    }
    
    # Спочатку спробуємо знайти існуючих одержувачів
    recipients_url = f"{base_url}/v1/accounts?profile={profile_id}"
    
    try:
        recipients_response = requests.get(recipients_url, headers=headers)
        
        recipient_id = None
        if recipients_response.status_code == 200:
            recipients = recipients_response.json()
            logger.info(f"Знайдено {len(recipients)} одержувачів")
            
            # Шукаємо одержувача з потрібною валютою
            for recipient in recipients:
                if recipient.get("currency") == currency and recipient.get("type") == "balance":
                    recipient_id = recipient.get("id")
                    logger.info(f"Знайдено існуючого одержувача з ID: {recipient_id}")
                    return recipient
        
        # Якщо одержувача не знайдено, створюємо нового
        if not recipient_id:
            logger.info("Створення нового одержувача")
            recipient_url = f"{base_url}/v1/accounts"
            recipient_payload = {
                "profile": profile_id,
                "accountHolderName": "ContentAI Test",
                "currency": currency,
                "type": "balance"
            }
            
            recipient_response = requests.post(recipient_url, headers=headers, json=recipient_payload)
            
            if recipient_response.status_code == 200:
                recipient = recipient_response.json()
                logger.info(f"Створено нового одержувача з ID: {recipient.get('id')}")
                return recipient
            else:
                logger.error(f"Помилка при створенні одержувача. Код відповіді: {recipient_response.status_code}")
                logger.error(f"Відповідь: {recipient_response.text}")
                return None
    except Exception as e:
        logger.error(f"Виникла помилка: {str(e)}")
        return None

# Тест 3: Створення переказу
def test_create_transfer(quote_id, recipient_id):
    logger.info(f"Тест 3: Створення переказу з котируванням {quote_id} та одержувачем {recipient_id}")
    
    reference = f"CONTENTAI-TEST-{uuid.uuid4().hex[:8].upper()}"
    
    transfer_url = f"{base_url}/v1/transfers"
    headers = {
        "Authorization": f"Bearer {wise_api_key}",
        "Content-Type": "application/json"
    }
    
    transfer_payload = {
        "targetAccount": recipient_id,
        "quoteUuid": quote_id,
        "customerTransactionId": reference,
        "details": {
            "reference": reference,
            "transferPurpose": "ContentAI Test",
            "sourceOfFunds": "verification.source.of.funds.other"
        }
    }
    
    try:
        response = requests.post(transfer_url, headers=headers, json=transfer_payload)
        
        if response.status_code == 200:
            transfer = response.json()
            logger.info(f"Переказ успішно створено з ID: {transfer.get('id')}")
            return transfer
        else:
            logger.error(f"Помилка при створенні переказу. Код відповіді: {response.status_code}")
            logger.error(f"Відповідь: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Виникла помилка: {str(e)}")
        return None

# Тест 4: Перевірка статусу переказу
def test_check_transfer_status(transfer_id):
    logger.info(f"Тест 4: Перевірка статусу переказу з ID {transfer_id}")
    
    url = f"{base_url}/v1/transfers/{transfer_id}"
    headers = {
        "Authorization": f"Bearer {wise_api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            transfer = response.json()
            status = transfer.get("status")
            logger.info(f"Статус переказу {transfer_id}: {status}")
            return transfer
        else:
            logger.error(f"Помилка при перевірці статусу переказу. Код відповіді: {response.status_code}")
            logger.error(f"Відповідь: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Виникла помилка: {str(e)}")
        return None

# Запуск тестів
if __name__ == "__main__":
    logger.info("Початок тестування Wise API для створення платежу")
    
    # Тест 1: Створення котирування
    quote = test_create_quote(amount=1.00, currency="USD")
    
    if quote:
        quote_id = quote.get("id")
        
        # Тест 2: Пошук або створення одержувача
        recipient = test_find_or_create_recipient(currency="USD")
        
        if recipient:
            recipient_id = recipient.get("id")
            
            # Тест 3: Створення переказу
            transfer = test_create_transfer(quote_id, recipient_id)
            
            if transfer:
                transfer_id = transfer.get("id")
                
                # Тест 4: Перевірка статусу переказу
                # Перевіряємо статус кілька разів з інтервалом
                for i in range(3):
                    transfer_status = test_check_transfer_status(transfer_id)
                    if transfer_status and transfer_status.get("status") == "completed":
                        break
                    logger.info(f"Очікування оновлення статусу переказу... ({i+1}/3)")
                    time.sleep(5)  # Чекаємо 5 секунд перед наступною перевіркою
    
    logger.info("Завершення тестування Wise API для створення платежу") 