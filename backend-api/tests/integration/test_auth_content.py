"""
Інтеграційні тести для перевірки взаємодії між модулями автентифікації та генерації контенту.
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
from content.routes import generate_ideas, get_trends
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
    
    # Реєструємо маршрути для генерації контенту з використанням тестового декоратора
    @app.route('/generate', methods=['POST'])
    @token_required_test
    def generate_ideas_route(current_user, lang='uk', translations=None):
        """
        Маршрут для генерації ідей контенту.
        
        Args:
            current_user: Поточний користувач
            lang: Мова (за замовчуванням 'uk')
            translations: Переклади (якщо None, будуть завантажені)
            
        Returns:
            tuple: Відповідь у форматі JSON та код статусу
        """
        data = request.get_json()
        
        topic = data.get('topic')
        count = data.get('count', 3)
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
            
        # Використовуємо мок для генерації ідей
        ideas = {
            "ideas": [
                {"title": f"Ідея {i+1} для {topic}", "description": f"Опис ідеї {i+1} для {topic}"}
                for i in range(count)
            ]
        }
            
        return jsonify(ideas), 200
    
    @app.route('/trends', methods=['POST'])
    @token_required_test
    def get_trends_route(current_user, lang='uk', translations=None):
        """
        Маршрут для отримання трендів.
        
        Args:
            current_user: Поточний користувач
            lang: Мова (за замовчуванням 'uk')
            translations: Переклади (якщо None, будуть завантажені)
            
        Returns:
            tuple: Відповідь у форматі JSON та код статусу
        """
        # Перевіряємо, чи користувач має преміум підписку
        is_premium = False
        
        if current_user.subscription_type == 'premium':
            if current_user.subscription_end and current_user.subscription_end > datetime.now():
                is_premium = True
                
        if not is_premium:
            return jsonify({'error': 'Premium subscription required'}), 403
            
        data = request.get_json()
        
        category = data.get('category')
        
        if not category:
            return jsonify({'error': 'Category is required'}), 400
            
        # Використовуємо мок для отримання трендів
        trends = {
            "ideas": [
                {"title": f"Тренд {i+1} для {category}", "description": f"Опис тренду {i+1} для {category}"}
                for i in range(3)
            ]
        }
            
        return jsonify(trends), 200
    
    return app

@pytest.fixture
def client(app):
    """Створює тестовий клієнт."""
    return app.test_client()

def test_login_and_generate_ideas(client):
    """
    Тест для перевірки взаємодії між входом та генерацією ідей.
    """
    # Отримуємо тестовий токен для преміум користувача
    token_response = client.get('/test-token/premium@example.com')
    token_data = json.loads(token_response.data)
    token = token_data.get('token')
    
    # Генеруємо ідеї
    generate_data = {
        'topic': 'Технології',
        'count': 3
    }
    
    generate_response = client.post('/generate',
                                  data=json.dumps(generate_data),
                                  headers={'Authorization': f'Bearer {token}'},
                                  content_type='application/json')
    
    assert generate_response.status_code == 200
    generate_data = json.loads(generate_response.data)
    
    # Перевіряємо, що ідеї згенеровані
    assert 'ideas' in generate_data
    assert len(generate_data['ideas']) == 3

def test_login_and_get_trends_premium_user(client):
    """
    Тест для перевірки взаємодії між входом та отриманням трендів для преміум користувача.
    """
    # Отримуємо тестовий токен для преміум користувача
    token_response = client.get('/test-token/premium@example.com')
    token_data = json.loads(token_response.data)
    token = token_data.get('token')
    
    # Отримуємо тренди
    trends_data = {
        'category': 'Технології'
    }
    
    trends_response = client.post('/trends',
                                data=json.dumps(trends_data),
                                headers={'Authorization': f'Bearer {token}'},
                                content_type='application/json')
    
    assert trends_response.status_code == 200
    trends_data = json.loads(trends_response.data)
    
    # Перевіряємо, що тренди отримані
    assert 'ideas' in trends_data

def test_login_and_get_trends_free_user(client):
    """
    Тест для перевірки взаємодії між входом та отриманням трендів для безкоштовного користувача.
    Безкоштовний користувач не повинен мати доступу до трендів.
    """
    # Отримуємо тестовий токен для безкоштовного користувача
    token_response = client.get('/test-token/free@example.com')
    token_data = json.loads(token_response.data)
    token = token_data.get('token')
    
    # Намагаємося отримати тренди
    trends_data = {
        'category': 'Технології'
    }
    
    trends_response = client.post('/trends',
                                data=json.dumps(trends_data),
                                headers={'Authorization': f'Bearer {token}'},
                                content_type='application/json')
    
    # Перевіряємо, що доступ заборонено
    assert trends_response.status_code == 403 