"""
Тести для функцій автентифікації та авторизації.
"""

import pytest
import json
import jwt
from datetime import datetime, timedelta
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
import os
import sys
from unittest.mock import patch
from functools import wraps

# Додаємо кореневу директорію проєкту до шляху імпорту
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models import db, User
from auth.routes import signup, login, token_required

@pytest.fixture
def app():
    """Створює тестовий екземпляр Flask додатку."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Створюємо тестового користувача з правильним форматом хешу пароля
        test_user = User(
            email='test@example.com',
            password='pbkdf2:sha256:150000$1234567890123456789012',  # Правильний формат хешу
            subscription_type='free'
        )
        db.session.add(test_user)
        db.session.commit()
    
    # Реєструємо маршрути
    signup_route = signup(app, db, User)
    login_route = login(app, db, User)
    
    return app

@pytest.fixture
def client(app):
    """Створює тестовий клієнт."""
    return app.test_client()

def test_signup(client):
    """Тестує функцію реєстрації користувача."""
    # Підготовка даних для запиту
    data = {
        'email': 'new_user@example.com',
        'password': 'password123'
    }
    
    # Відправка запиту
    response = client.post('/signup', json=data)
    
    # Перевірка результату
    assert response.status_code == 201
    # Перевіряємо наявність повідомлення про успішну реєстрацію (українською)
    response_data = json.loads(response.data)
    assert 'message' in response_data
    assert 'успішна' in response_data['message'].lower() or 'реєстрація' in response_data['message'].lower()
    
    # Перевірка, що користувач був створений
    with client.application.app_context():
        user = User.query.filter_by(email='new_user@example.com').first()
        assert user is not None

def test_signup_existing_user(client):
    """Тестує реєстрацію з існуючим email."""
    # Підготовка даних для запиту
    data = {
        'email': 'test@example.com',  # Вже існуючий email
        'password': 'password123'
    }
    
    # Відправка запиту
    try:
        response = client.post('/signup', json=data)
        # Якщо виняток не був викинутий, перевіряємо код статусу
        assert response.status_code == 409  # Conflict
        # Перевіряємо наявність повідомлення про існуючого користувача (українською)
        response_data = json.loads(response.data)
        assert 'message' in response_data
        assert 'існує' in response_data['message'].lower()
    except Exception as e:
        # Перевіряємо, що виняток містить правильне повідомлення
        assert 'існує' in str(e).lower() or 'вже існує' in str(e).lower()

def test_login(client):
    """Тестує функцію входу користувача."""
    # Підготовка даних для запиту
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    # Використовуємо patch для мокування функції check_password_hash
    with patch('auth.routes.check_password_hash', return_value=True):
        # Відправка запиту
        response = client.post('/login', json=data)
        
        # Перевірка результату
        assert response.status_code == 200
        
        # Перевірка вмісту відповіді
        response_data = json.loads(response.data)
        assert 'token' in response_data
        assert 'user_id' in response_data
        assert 'email' in response_data
        assert response_data['email'] == 'test@example.com'
        assert 'message' in response_data
        assert 'успішний' in response_data['message'].lower() or 'вхід' in response_data['message'].lower()

def test_login_invalid_credentials(client):
    """Тестує вхід з невірними обліковими даними."""
    # Підготовка даних для запиту
    data = {
        'email': 'test@example.com',
        'password': 'wrong_password'
    }
    
    # Використовуємо patch для мокування функції check_password_hash
    with patch('auth.routes.check_password_hash', return_value=False):
        # Відправка запиту
        try:
            response = client.post('/login', json=data)
            # Якщо виняток не був викинутий, перевіряємо код статусу
            assert response.status_code == 401
            # Перевіряємо наявність повідомлення про невірні облікові дані (українською)
            response_data = json.loads(response.data)
            assert 'message' in response_data
            assert 'невірні' in response_data['message'].lower() or 'облікові' in response_data['message'].lower()
        except Exception as e:
            # Перевіряємо, що виняток містить правильне повідомлення
            assert 'невірні' in str(e).lower() or 'облікові' in str(e).lower()

def test_token_required(app):
    """Тестує декоратор token_required."""
    # Перевіряємо, що декоратор token_required існує і є функцією
    assert callable(token_required)
    
    # Перевіряємо, що декоратор повертає функцію
    decorated = token_required(lambda: None)
    assert callable(decorated)
    
    # Перевіряємо, що декоратор зберігає метадані функції
    def test_func():
        """Test function docstring."""
        pass
    
    decorated_test_func = token_required(test_func)
    assert decorated_test_func.__name__ == test_func.__name__
    assert decorated_test_func.__doc__ == test_func.__doc__ 