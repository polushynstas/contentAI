"""
Модуль для обробки помилок у застосунку.

Цей модуль надає функції для обробки різних типів помилок
та генерації відповідних HTTP відповідей.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException
from utils.logger import log_exception, app_logger

class APIError(Exception):
    """Базовий клас для помилок API."""
    status_code = 500
    error_code = 'internal_error'
    message = 'Внутрішня помилка сервера'
    
    def __init__(self, message=None, error_code=None, status_code=None, payload=None):
        super().__init__(message or self.message)
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        self.status_code = status_code or self.status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or {})
        rv['error'] = self.error_code
        rv['message'] = self.message
        return rv

class BadRequestError(APIError):
    """Помилка неправильного запиту."""
    status_code = 400
    error_code = 'bad_request'
    message = 'Неправильний запит'

class UnauthorizedError(APIError):
    """Помилка неавторизованого доступу."""
    status_code = 401
    error_code = 'unauthorized'
    message = 'Необхідна авторизація'

class ForbiddenError(APIError):
    """Помилка забороненого доступу."""
    status_code = 403
    error_code = 'forbidden'
    message = 'Доступ заборонено'

class NotFoundError(APIError):
    """Помилка ресурс не знайдено."""
    status_code = 404
    error_code = 'not_found'
    message = 'Ресурс не знайдено'

class ValidationError(BadRequestError):
    """Помилка валідації даних."""
    error_code = 'validation_error'
    message = 'Помилка валідації даних'

class DatabaseError(APIError):
    """Помилка бази даних."""
    error_code = 'database_error'
    message = 'Помилка бази даних'

class ExternalServiceError(APIError):
    """Помилка зовнішнього сервісу."""
    error_code = 'external_service_error'
    message = 'Помилка зовнішнього сервісу'

def register_error_handlers(app):
    """
    Реєструє обробники помилок для Flask додатку.
    
    Args:
        app: Екземпляр Flask додатку
    """
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Обробник для помилок API."""
        log_exception(app_logger, error)
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Обробник для HTTP помилок."""
        log_exception(app_logger, error)
        response = jsonify({
            'error': str(error.__class__.__name__),
            'message': str(error)
        })
        response.status_code = error.code
        return response
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Обробник для загальних помилок."""
        log_exception(app_logger, error)
        response = jsonify({
            'error': 'internal_error',
            'message': 'Внутрішня помилка сервера'
        })
        response.status_code = 500
        return response
    
    app_logger.info("Зареєстровано обробники помилок")

def validate_request_data(data, required_fields):
    """
    Валідує дані запиту.
    
    Args:
        data: Дані запиту
        required_fields: Список обов'язкових полів
        
    Raises:
        ValidationError: Якщо відсутні обов'язкові поля
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(
            message=f"Відсутні обов'язкові поля: {', '.join(missing_fields)}",
            payload={'missing_fields': missing_fields}
        )

def handle_database_error(e, context=None):
    """
    Обробляє помилку бази даних.
    
    Args:
        e: Виключення
        context: Додатковий контекст
        
    Raises:
        DatabaseError: Обгорнута помилка бази даних
    """
    log_exception(app_logger, e, context)
    raise DatabaseError(message=str(e), payload=context)

def handle_external_service_error(e, service_name, context=None):
    """
    Обробляє помилку зовнішнього сервісу.
    
    Args:
        e: Виключення
        service_name: Назва сервісу
        context: Додатковий контекст
        
    Raises:
        ExternalServiceError: Обгорнута помилка зовнішнього сервісу
    """
    error_context = {'service': service_name}
    if context:
        error_context.update(context)
    
    log_exception(app_logger, e, error_context)
    raise ExternalServiceError(
        message=f"Помилка сервісу {service_name}: {str(e)}",
        payload=error_context
    ) 