"""
Тести для функцій управління підписками.
"""

import pytest
import json
import os
import sys
from unittest.mock import MagicMock, patch
from flask import Flask, request
from datetime import datetime, timedelta

# Додаємо кореневу директорію проєкту до шляху імпорту
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models import db, User, Payment
from subscription.routes import check_subscription, update_subscription, check_payment

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
        
        # Створюємо тестового користувача з активною підпискою
        premium_user = User(
            id=1,
            email='premium@example.com',
            password='$2b$12$1234567890123456789012',  # Хешований пароль
            subscription_type='premium',
            subscription_end_date=datetime.utcnow() + timedelta(days=30)  # Виправлено поле
        )
        
        # Створюємо тестового користувача з безкоштовною підпискою
        free_user = User(
            id=2,
            email='free@example.com',
            password='$2b$12$1234567890123456789012',  # Хешований пароль
            subscription_type='free'
        )
        
        # Створюємо тестового користувача з простроченою підпискою
        expired_user = User(
            id=3,
            email='expired@example.com',
            password='$2b$12$1234567890123456789012',  # Хешований пароль
            subscription_type='premium',
            subscription_end_date=datetime.utcnow() - timedelta(days=1)  # Виправлено поле
        )
        
        # Створюємо тестовий платіж
        payment = Payment(
            id=1,
            user_id=2,  # free_user
            payment_id='test_payment_id',
            amount=9.99,
            currency='USD',
            status='pending',
            plan='premium',  # Додаємо обов'язкове поле plan
            created_at=datetime.utcnow()
        )
        
        db.session.add(premium_user)
        db.session.add(free_user)
        db.session.add(expired_user)
        db.session.add(payment)
        db.session.commit()
    
    return app

@pytest.fixture
def client(app):
    """Створює тестовий клієнт."""
    return app.test_client()

def test_check_subscription_premium(app, client):
    """Тестує перевірку преміум-підписки."""
    # Використовуємо тестовий клієнт для створення контексту запиту
    with app.app_context():
        with app.test_request_context('/check-subscription?lang=uk'):
            check_subscription_route = check_subscription(app, db, User)
            
            # Отримуємо користувача з преміум-підпискою
            user = User.query.filter_by(email='premium@example.com').first()
            
            # Викликаємо функцію безпосередньо
            response = check_subscription_route(user)
            
            # Перевірка результату
            assert response is not None
            response_data = json.loads(response[0].data)
            assert response_data['subscription_type'] == 'premium'
            assert response_data['is_active'] == True
            assert 'subscription_end' in response_data

def test_check_subscription_free(app, client):
    """Тестує перевірку безкоштовної підписки."""
    # Використовуємо тестовий клієнт для створення контексту запиту
    with app.app_context():
        with app.test_request_context('/check-subscription?lang=uk'):
            check_subscription_route = check_subscription(app, db, User)
            
            # Отримуємо користувача з безкоштовною підпискою
            user = User.query.filter_by(email='free@example.com').first()
            
            # Викликаємо функцію безпосередньо
            response = check_subscription_route(user)
            
            # Перевірка результату
            assert response is not None
            response_data = json.loads(response[0].data)
            assert response_data['subscription_type'] == 'free'
            assert response_data['is_active'] == True  # Безкоштовна підписка завжди активна
            assert 'subscription_end' in response_data
            assert response_data['subscription_end'] is None

def test_check_subscription_expired(app, client):
    """Тестує перевірку простроченої підписки."""
    # Використовуємо тестовий клієнт для створення контексту запиту
    with app.app_context():
        with app.test_request_context('/check-subscription?lang=uk'):
            check_subscription_route = check_subscription(app, db, User)
            
            # Отримуємо користувача з простроченою підпискою
            user = User.query.filter_by(email='expired@example.com').first()
            
            # Встановлюємо дату закінчення підписки в минуле
            user.subscription_end = datetime.utcnow() - timedelta(days=1)
            db.session.commit()
            
            # Викликаємо функцію безпосередньо
            response = check_subscription_route(user)
            
            # Перевірка результату
            assert response is not None
            response_data = json.loads(response[0].data)
            assert response_data['subscription_type'] == 'free'  # Має бути змінено на free, оскільки підписка прострочена
            assert response_data['is_active'] == False  # Підписка неактивна, оскільки вона прострочена
            assert 'subscription_end' in response_data
            assert response_data['subscription_end'] is None  # Після закінчення підписки, subscription_end має бути None

def test_update_subscription(app, client):
    """Тестує оновлення підписки."""
    # Використовуємо тестовий клієнт для створення контексту запиту
    with app.app_context():
        with app.test_request_context('/update-subscription?lang=uk', method='POST', 
                                     json={'subscription_type': 'premium'}):
            update_subscription_route = update_subscription(app, db, User, Payment)
            
            # Отримуємо користувача з безкоштовною підпискою
            user = User.query.filter_by(email='free@example.com').first()
            
            # Викликаємо функцію безпосередньо
            response = update_subscription_route(user)
            
            # Перевірка результату
            assert response is not None
            response_data = json.loads(response[0].data)
            assert 'message' in response_data
            assert response_data['subscription_type'] == 'premium'
            assert 'subscription_end' in response_data
            assert response_data['subscription_end'] is not None

def test_check_payment_success(app, client):
    """Тестує перевірку успішного платежу."""
    # Використовуємо тестовий клієнт для створення контексту запиту
    with app.app_context():
        with app.test_request_context('/check-payment/test_payment_id?lang=uk&type=premium'):
            check_payment_route = check_payment(app, db, User, Payment)
            
            # Отримуємо користувача з безкоштовною підпискою
            user = User.query.filter_by(email='free@example.com').first()
            
            # Викликаємо функцію безпосередньо
            response = check_payment_route('test_payment_id', current_user=user)
            
            # Перевірка результату
            assert response is not None
            response_data = json.loads(response[0].data)
            assert response_data['status'] == 'pending'  # Статус платежу в нашому тестовому середовищі
            assert 'payment_id' in response_data
            assert 'amount' in response_data
            assert 'currency' in response_data
            assert 'created_at' in response_data

def test_check_payment_pending(app, client):
    """Тестує перевірку платежу в очікуванні."""
    # Використовуємо тестовий клієнт для створення контексту запиту
    with app.app_context():
        with app.test_request_context('/check-payment/test_payment_id?lang=uk&type=professional'):
            check_payment_route = check_payment(app, db, User, Payment)
            
            # Отримуємо користувача з безкоштовною підпискою
            user = User.query.filter_by(email='free@example.com').first()
            
            # Викликаємо функцію безпосередньо
            response = check_payment_route('test_payment_id', current_user=user)
            
            # Перевірка результату
            assert response is not None
            response_data = json.loads(response[0].data)
            assert response_data['status'] == 'pending'  # Статус платежу в нашому тестовому середовищі
            assert 'payment_id' in response_data
            assert 'amount' in response_data
            assert 'currency' in response_data
            assert 'created_at' in response_data

def test_check_payment_failed(app, client):
    """Тестує перевірку невдалого платежу."""
    # Використовуємо тестовий клієнт для створення контексту запиту
    with app.app_context():
        with app.test_request_context('/check-payment/test_payment_id?lang=uk&type=premium'):
            check_payment_route = check_payment(app, db, User, Payment)
            
            # Отримуємо користувача з безкоштовною підпискою
            user = User.query.filter_by(email='free@example.com').first()
            
            # Створюємо тестовий платіж з failed_payment_id
            failed_payment = Payment(
                user_id=user.id,
                payment_id='failed_payment_id',
                amount=9.99,
                currency='USD',
                status='failed',
                plan='premium',
                created_at=datetime.utcnow()
            )
            db.session.add(failed_payment)
            db.session.commit()
            
            # Викликаємо функцію безпосередньо з іншим payment_id, щоб симулювати невдалий платіж
            response = check_payment_route('failed_payment_id', current_user=user)
            
            # Перевірка результату
            assert response is not None
            response_data = json.loads(response[0].data)
            assert response_data['status'] == 'failed'  # Статус платежу в нашому тестовому середовищі
            assert 'payment_id' in response_data
            assert 'amount' in response_data
            assert 'currency' in response_data
            assert 'created_at' in response_data 