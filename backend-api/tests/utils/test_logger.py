"""
Тести для модуля логування.
"""

import pytest
import logging
import os
from unittest.mock import patch, MagicMock
from flask import Flask, request, Response
from utils.logger import (
    get_logger, log_exception, log_request, log_response,
    auth_logger, content_logger, subscription_logger, app_logger
)

@pytest.fixture
def app():
    """Створює тестовий екземпляр Flask додатку."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Створює тестовий клієнт."""
    return app.test_client()

def test_get_logger():
    """Тест для функції get_logger."""
    logger = get_logger('test_logger')
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'test_logger'
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0

def test_predefined_loggers():
    """Тест для попередньо визначених логерів."""
    assert isinstance(auth_logger, logging.Logger)
    assert isinstance(content_logger, logging.Logger)
    assert isinstance(subscription_logger, logging.Logger)
    assert isinstance(app_logger, logging.Logger)
    
    assert auth_logger.name == 'auth'
    assert content_logger.name == 'content'
    assert subscription_logger.name == 'subscription'
    assert app_logger.name == 'app'

@patch('utils.logger.logging.Logger.error')
def test_log_exception(mock_error):
    """Тест для функції log_exception."""
    logger = get_logger('test_exception')
    exception = ValueError("Тестова помилка")
    context = {'user_id': 123, 'action': 'test'}
    
    log_exception(logger, exception, context)
    
    # Перевіряємо, що метод error був викликаний двічі
    assert mock_error.call_count == 2
    
    # Перевіряємо перший виклик (повідомлення про помилку)
    args, _ = mock_error.call_args_list[0]
    assert "Exception: Тестова помилка" in args[0]
    assert "Context: {'user_id': 123, 'action': 'test'}" in args[0]

def test_log_request(app):
    """Тест для функції log_request."""
    with app.test_request_context('/test?param=value', method='POST', 
                                 headers={'User-Agent': 'Test Agent'}):
        with patch('utils.logger.logging.Logger.info') as mock_info:
            logger = get_logger('test_request')
            log_request(logger, request)
            
            # Перевіряємо, що метод info був викликаний
            mock_info.assert_called_once()
            
            # Перевіряємо аргументи виклику
            args, _ = mock_info.call_args
            assert 'Request:' in args[0]
            assert "'method': 'POST'" in args[0]
            assert "'path': '/test'" in args[0]
            assert "'user_agent': 'Test Agent'" in args[0]

def test_log_request_with_body(app):
    """Тест для функції log_request з включенням тіла запиту."""
    with app.test_request_context('/test', method='POST', 
                                 json={'key': 'value'},
                                 headers={'User-Agent': 'Test Agent'}):
        with patch('utils.logger.logging.Logger.info') as mock_info:
            logger = get_logger('test_request')
            log_request(logger, request, include_body=True)
            
            # Перевіряємо, що метод info був викликаний
            mock_info.assert_called_once()
            
            # Перевіряємо аргументи виклику
            args, _ = mock_info.call_args
            assert 'Request:' in args[0]
            assert "'body': {'key': 'value'}" in args[0]

def test_log_response():
    """Тест для функції log_response."""
    with patch('utils.logger.logging.Logger.info') as mock_info:
        logger = get_logger('test_response')
        response = Response('Test response', status=200)
        log_response(logger, response, 123.45)
        
        # Перевіряємо, що метод info був викликаний
        mock_info.assert_called_once()
        
        # Перевіряємо аргументи виклику
        args, _ = mock_info.call_args
        assert 'Response:' in args[0]
        assert "'status_code': 200" in args[0]
        assert "'request_time': '123.45ms'" in args[0]

def test_log_directory_creation():
    """Тест для створення директорії для логів."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    assert os.path.exists(log_dir)
    
    # Перевіряємо, що файли логів створені
    assert os.path.exists(os.path.join(log_dir, 'app.log'))
    assert os.path.exists(os.path.join(log_dir, 'error.log')) 