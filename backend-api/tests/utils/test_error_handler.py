"""
Тести для модуля обробки помилок.
"""

import pytest
from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, BadRequest
from utils.error_handler import (
    APIError, BadRequestError, UnauthorizedError, ForbiddenError, 
    NotFoundError, ValidationError, DatabaseError, ExternalServiceError,
    register_error_handlers, validate_request_data
)

@pytest.fixture
def app():
    """Створює тестовий екземпляр Flask додатку."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Реєстрація обробників помилок
    register_error_handlers(app)
    
    # Тестовий маршрут, який викликає різні помилки
    @app.route('/test-api-error')
    def test_api_error():
        raise APIError(message="Тестова помилка API")
    
    @app.route('/test-bad-request')
    def test_bad_request():
        raise BadRequestError(message="Тестова помилка неправильного запиту")
    
    @app.route('/test-unauthorized')
    def test_unauthorized():
        raise UnauthorizedError(message="Тестова помилка неавторизованого доступу")
    
    @app.route('/test-forbidden')
    def test_forbidden():
        raise ForbiddenError(message="Тестова помилка забороненого доступу")
    
    @app.route('/test-not-found')
    def test_not_found():
        raise NotFoundError(message="Тестова помилка ресурс не знайдено")
    
    @app.route('/test-validation-error')
    def test_validation_error():
        raise ValidationError(message="Тестова помилка валідації даних")
    
    @app.route('/test-database-error')
    def test_database_error():
        raise DatabaseError(message="Тестова помилка бази даних")
    
    @app.route('/test-external-service-error')
    def test_external_service_error():
        raise ExternalServiceError(message="Тестова помилка зовнішнього сервісу")
    
    @app.route('/test-http-exception')
    def test_http_exception():
        raise NotFound("Тестова помилка HTTP")
    
    @app.route('/test-generic-exception')
    def test_generic_exception():
        raise Exception("Тестова загальна помилка")
    
    return app

@pytest.fixture
def client(app):
    """Створює тестовий клієнт."""
    return app.test_client()

def test_api_error(client):
    """Тест для APIError."""
    response = client.get('/test-api-error')
    assert response.status_code == 500
    data = response.get_json()
    assert data['error'] == 'internal_error'
    assert data['message'] == 'Тестова помилка API'

def test_bad_request_error(client):
    """Тест для BadRequestError."""
    response = client.get('/test-bad-request')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'bad_request'
    assert data['message'] == 'Тестова помилка неправильного запиту'

def test_unauthorized_error(client):
    """Тест для UnauthorizedError."""
    response = client.get('/test-unauthorized')
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == 'unauthorized'
    assert data['message'] == 'Тестова помилка неавторизованого доступу'

def test_forbidden_error(client):
    """Тест для ForbiddenError."""
    response = client.get('/test-forbidden')
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'forbidden'
    assert data['message'] == 'Тестова помилка забороненого доступу'

def test_not_found_error(client):
    """Тест для NotFoundError."""
    response = client.get('/test-not-found')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'not_found'
    assert data['message'] == 'Тестова помилка ресурс не знайдено'

def test_validation_error(client):
    """Тест для ValidationError."""
    response = client.get('/test-validation-error')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'validation_error'
    assert data['message'] == 'Тестова помилка валідації даних'

def test_database_error(client):
    """Тест для DatabaseError."""
    response = client.get('/test-database-error')
    assert response.status_code == 500
    data = response.get_json()
    assert data['error'] == 'database_error'
    assert data['message'] == 'Тестова помилка бази даних'

def test_external_service_error(client):
    """Тест для ExternalServiceError."""
    response = client.get('/test-external-service-error')
    assert response.status_code == 500
    data = response.get_json()
    assert data['error'] == 'external_service_error'
    assert data['message'] == 'Тестова помилка зовнішнього сервісу'

def test_http_exception(client):
    """Тест для HTTP помилок."""
    response = client.get('/test-http-exception')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'NotFound'
    assert 'Тестова помилка HTTP' in data['message']

def test_generic_exception(client):
    """Тест для загальних помилок."""
    response = client.get('/test-generic-exception')
    assert response.status_code == 500
    data = response.get_json()
    assert data['error'] == 'internal_error'
    assert data['message'] == 'Внутрішня помилка сервера'

def test_validate_request_data():
    """Тест для функції validate_request_data."""
    # Валідні дані
    data = {'field1': 'value1', 'field2': 'value2'}
    validate_request_data(data, ['field1', 'field2'])
    
    # Відсутні поля
    with pytest.raises(ValidationError) as excinfo:
        validate_request_data(data, ['field1', 'field2', 'field3'])
    assert 'field3' in str(excinfo.value)
    
    # Порожні дані
    with pytest.raises(ValidationError):
        validate_request_data({}, ['field1', 'field2']) 