"""
Модуль для логування подій у застосунку.

Цей модуль надає функції для логування подій різних рівнів
та налаштування логування для різних частин застосунку.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import traceback
from datetime import datetime

# Створюємо директорію для логів, якщо вона не існує
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Налаштування форматування логів
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Створюємо файловий обробник для всіх логів
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    maxBytes=10485760,  # 10 MB
    backupCount=10
)
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.INFO)

# Створюємо файловий обробник для помилок
error_handler = RotatingFileHandler(
    os.path.join(log_dir, 'error.log'),
    maxBytes=10485760,  # 10 MB
    backupCount=10
)
error_handler.setFormatter(log_format)
error_handler.setLevel(logging.ERROR)

# Створюємо консольний обробник
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.INFO)

def get_logger(name):
    """
    Отримує логер з вказаним ім'ям.
    
    Args:
        name: Ім'я логера (зазвичай __name__ модуля)
        
    Returns:
        logging.Logger: Налаштований логер
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Додаємо обробники, якщо вони ще не додані
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)
    
    return logger

def log_exception(logger, e, context=None):
    """
    Логує виключення з детальною інформацією.
    
    Args:
        logger: Логер для запису
        e: Виключення
        context: Додатковий контекст (словник)
    """
    error_message = f"Exception: {str(e)}"
    if context:
        error_message += f", Context: {context}"
    
    logger.error(error_message)
    logger.error(traceback.format_exc())

def log_request(logger, request, include_body=False):
    """
    Логує інформацію про HTTP запит.
    
    Args:
        logger: Логер для запису
        request: Об'єкт запиту Flask
        include_body: Чи включати тіло запиту (за замовчуванням False)
    """
    log_data = {
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string,
        'timestamp': datetime.now().isoformat()
    }
    
    if include_body and request.is_json:
        log_data['body'] = request.get_json()
    
    logger.info(f"Request: {log_data}")

def log_response(logger, response, request_time=None):
    """
    Логує інформацію про HTTP відповідь.
    
    Args:
        logger: Логер для запису
        response: Об'єкт відповіді Flask
        request_time: Час виконання запиту (якщо доступний)
    """
    log_data = {
        'status_code': response.status_code,
        'content_length': response.content_length,
        'timestamp': datetime.now().isoformat()
    }
    
    if request_time:
        log_data['request_time'] = f"{request_time:.2f}ms"
    
    logger.info(f"Response: {log_data}")

# Створюємо логери для різних модулів
auth_logger = get_logger('auth')
content_logger = get_logger('content')
subscription_logger = get_logger('subscription')
app_logger = get_logger('app') 