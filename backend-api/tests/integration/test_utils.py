"""
Утиліти для інтеграційних тестів.
"""

import jwt
import traceback
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g

def generate_password_hash(password):
    """
    Генерує хеш пароля для тестів.
    
    Args:
        password: Пароль для хешування
        
    Returns:
        str: Хеш пароля
    """
    from werkzeug.security import generate_password_hash
    # Використовуємо pbkdf2 замість scrypt, оскільки scrypt може бути недоступним
    return generate_password_hash(password, method='pbkdf2:sha256')

def token_required_test(f):
    """
    Декоратор для перевірки токена в тестах.
    
    Args:
        f: Функція, яку потрібно декорувати
        
    Returns:
        function: Декорована функція
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            from flask import current_app
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            from models import User, db
            
            # Виводимо інформацію для налагодження
            print(f"Decoded token: {data}")
            
            # Перевіряємо, чи існує користувач
            user_id = data.get('user_id')
            if not user_id:
                print("No user_id in token")
                return jsonify({'message': 'Invalid token: no user_id'}), 401
            
            # Отримуємо користувача
            current_user = User.query.filter_by(id=user_id).first()
            
            if not current_user:
                print(f"User with id {user_id} not found")
                # Виводимо всіх користувачів для налагодження
                all_users = User.query.all()
                print(f"All users: {[u.id for u in all_users]}")
                return jsonify({'message': 'User not found!'}), 401
            
            # Додаємо користувача до глобального контексту
            g.current_user = current_user
            
            # Передаємо користувача як аргумент
            return f(current_user=current_user, *args, **kwargs)
        except Exception as e:
            print(f"Error in token_required_test: {str(e)}")
            traceback.print_exc()
            return jsonify({'message': f'Token is invalid! Error: {str(e)}'}), 401
        
    return decorated

def register_test_routes(app, db, User):
    """
    Реєструє тестові маршрути.
    
    Args:
        app: Екземпляр Flask додатку
        db: Екземпляр бази даних
        User: Модель користувача
    """
    # Маршрут для отримання токена для тестування
    @app.route('/test-token/<email>', methods=['GET'])
    def get_test_token(email):
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'error': 'User not found'}, 404
        
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # Виводимо інформацію для налагодження
        print(f"Generated token for user {user.id} ({email}): {token}")
        
        return {'token': token}, 200 