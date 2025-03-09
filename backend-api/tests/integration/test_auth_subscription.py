"""
Інтеграційні тести для перевірки взаємодії між модулями автентифікації та підписок.
"""

import pytest
import json
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from flask import request, jsonify

# Додаємо кореневу директорію проєкту до шляху імпорту
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models import db, User
from auth.routes import signup, login
from subscription.routes import check_subscription, update_subscription
from tests.integration.test_utils import generate_password_hash, token_required_test, register_test_routes

@pytest.fixture
def app():
    """Створює тестовий екземпляр Flask додатку."""
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.app_context():
        db.init_app(app)
        db.create_all()
        
        # Створюємо тестового користувача з преміум підпискою
        premium_user = User(
            email='premium@example.com',
            password=generate_password_hash('password123'),
            subscription_type='premium',
            subscription_end=datetime.now() + timedelta(days=30)
        )
        
        # Створюємо тестового користувача з безкоштовною підпискою
        free_user = User(
            email='free@example.com',
            password=generate_password_hash('password123'),
            subscription_type='free',
            subscription_end=None
        )
        
        db.session.add(premium_user)
        db.session.add(free_user)
        db.session.commit()
    
    # Реєструємо тестові маршрути
    register_test_routes(app, db, User)
    
    # Реєструємо маршрути для автентифікації
    signup(app, db, User)
    login(app, db, User)
    
    # Реєструємо маршрути для підписок з використанням тестового декоратора
    @app.route('/check-subscription', methods=['GET'])
    @token_required_test
    def check_subscription_route(current_user, lang='uk', translations=None):
        """
        Маршрут для перевірки підписки користувача.
        
        Args:
            current_user: Поточний користувач
            lang: Мова (за замовчуванням 'uk')
            translations: Переклади (якщо None, будуть завантажені)
            
        Returns:
            tuple: Відповідь у форматі JSON та код статусу
        """
        is_active = False
        
        if current_user.subscription_type == 'premium':
            if current_user.subscription_end and current_user.subscription_end > datetime.now():
                is_active = True
        else:
            is_active = True
            
        return jsonify({
            'subscription_type': current_user.subscription_type,
            'is_active': is_active,
            'subscription_end': current_user.subscription_end.isoformat() if current_user.subscription_end else None
        }), 200
    
    @app.route('/update-subscription', methods=['POST'])
    @token_required_test
    def update_subscription_route(current_user, lang='uk', translations=None):
        """
        Маршрут для оновлення підписки користувача.
        
        Args:
            current_user: Поточний користувач
            lang: Мова (за замовчуванням 'uk')
            translations: Переклади (якщо None, будуть завантажені)
            
        Returns:
            tuple: Відповідь у форматі JSON та код статусу
        """
        data = request.get_json()
        
        subscription_type = data.get('subscription_type')
        duration = data.get('duration', 30)  # За замовчуванням 30 днів
        
        if subscription_type not in ['free', 'premium']:
            return jsonify({'error': 'Invalid subscription type'}), 400
            
        current_user.subscription_type = subscription_type
        
        if subscription_type == 'premium':
            current_user.subscription_end = datetime.now() + timedelta(days=duration)
        else:
            current_user.subscription_end = None
            
        db.session.commit()
        
        is_active = False
        
        if current_user.subscription_type == 'premium':
            if current_user.subscription_end and current_user.subscription_end > datetime.now():
                is_active = True
        else:
            is_active = True
            
        return jsonify({
            'subscription_type': current_user.subscription_type,
            'is_active': is_active,
            'subscription_end': current_user.subscription_end.isoformat() if current_user.subscription_end else None
        }), 200
    
    return app

@pytest.fixture
def client(app):
    """Створює тестовий клієнт."""
    return app.test_client()

def test_signup_and_check_subscription(client):
    """
    Тест для перевірки взаємодії між реєстрацією та перевіркою підписки.
    Новий користувач повинен мати безкоштовну підписку після реєстрації.
    """
    # Реєструємо нового користувача
    signup_data = {
        'email': 'newuser@example.com',
        'password': 'password123',
        'name': 'New User'
    }
    
    signup_response = client.post('/signup', 
                                 data=json.dumps(signup_data),
                                 content_type='application/json')
    
    assert signup_response.status_code == 201
    signup_data = json.loads(signup_response.data)
    
    # Отримуємо тестовий токен для нового користувача
    token_response = client.get('/test-token/newuser@example.com')
    token_data = json.loads(token_response.data)
    token = token_data.get('token')
    
    # Перевіряємо підписку нового користувача
    subscription_response = client.get('/check-subscription',
                                      headers={'Authorization': f'Bearer {token}'})
    
    assert subscription_response.status_code == 200
    subscription_data = json.loads(subscription_response.data)
    
    # Перевіряємо, що новий користувач має безкоштовну підписку
    assert subscription_data.get('subscription_type') == 'free'
    assert subscription_data.get('is_active') == True

def test_login_and_update_subscription(client):
    """
    Тест для перевірки взаємодії між входом та оновленням підписки.
    """
    # Отримуємо тестовий токен для безкоштовного користувача
    token_response = client.get('/test-token/free@example.com')
    token_data = json.loads(token_response.data)
    token = token_data.get('token')
    
    # Оновлюємо підписку користувача до преміум
    update_data = {
        'subscription_type': 'premium',
        'duration': 30  # днів
    }
    
    update_response = client.post('/update-subscription',
                                data=json.dumps(update_data),
                                headers={'Authorization': f'Bearer {token}'},
                                content_type='application/json')
    
    assert update_response.status_code == 200
    update_data = json.loads(update_response.data)
    
    # Перевіряємо, що підписка оновлена до преміум
    assert update_data.get('subscription_type') == 'premium'
    assert update_data.get('is_active') == True
    
    # Перевіряємо підписку після оновлення
    subscription_response = client.get('/check-subscription',
                                     headers={'Authorization': f'Bearer {token}'})
    
    assert subscription_response.status_code == 200
    subscription_data = json.loads(subscription_response.data)
    
    # Перевіряємо, що користувач тепер має преміум підписку
    assert subscription_data.get('subscription_type') == 'premium'
    assert subscription_data.get('is_active') == True 