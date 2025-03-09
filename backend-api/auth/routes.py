"""
Маршрути для автентифікації та авторизації.
"""

import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash

from utils.i18n import load_translations
from utils.error_handler import ValidationError, UnauthorizedError, ForbiddenError, NotFoundError
from models import User  # Додаємо прямий імпорт моделі User

def signup(app, db, User, logger=None):
    """
    Функція для реєстрації нового користувача.
    
    Args:
        app: Екземпляр Flask додатку
        db: Екземпляр бази даних
        User: Модель користувача
        logger: Логер для запису подій
        
    Returns:
        function: Функція-обробник маршруту /signup
    """
    @app.route('/signup', methods=['POST'])
    def signup_route():
        lang = request.args.get('lang', 'uk')
        translations = load_translations(lang)
        
        data = request.get_json()
        
        if not data:
            if logger:
                logger.warning("Спроба реєстрації з невірним запитом")
            raise ValidationError(message=translations.get('auth', {}).get('invalid_request', 'Невірний запит'))
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            if logger:
                logger.warning(f"Спроба реєстрації з відсутніми полями: email={bool(email)}, password={bool(password)}")
            raise ValidationError(message=translations.get('auth', {}).get('missing_fields', 'Відсутні обов\'язкові поля'))
            
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            if logger:
                logger.warning(f"Спроба реєстрації з існуючою електронною поштою: {email}")
            raise ValidationError(
                message=translations.get('auth', {}).get('user_exists', 'Користувач з такою електронною поштою вже існує'),
                status_code=409
            )
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(email=email, password=hashed_password, subscription_type='free')
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            token = jwt.encode({
                'user_id': new_user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            if logger:
                logger.info(f"Новий користувач зареєстрований: {email}")
            
            return jsonify({
                'message': translations.get('auth', {}).get('signup_success', 'Реєстрація успішна'),
                'token': token
            }), 201
        except Exception as e:
            db.session.rollback()
            if logger:
                logger.error(f"Помилка при реєстрації користувача {email}: {str(e)}")
            raise
    
    return signup_route

def login(app, db, User, logger=None):
    """
    Функція для входу користувача.
    
    Args:
        app: Екземпляр Flask додатку
        db: Екземпляр бази даних
        User: Модель користувача
        logger: Логер для запису подій
        
    Returns:
        function: Функція-обробник маршруту /login
    """
    @app.route('/login', methods=['POST'])
    def login_route():
        lang = request.args.get('lang', 'uk')
        translations = load_translations(lang)
        
        auth = request.get_json()
        
        if not auth or not auth.get('email') or not auth.get('password'):
            if logger:
                logger.warning("Спроба входу з невірними даними")
            raise ValidationError(message=translations.get('auth', {}).get('invalid_credentials', 'Невірні дані для входу'))
            
        user = User.query.filter_by(email=auth.get('email')).first()
        
        if not user:
            if logger:
                logger.warning(f"Спроба входу з неіснуючою електронною поштою: {auth.get('email')}")
            raise UnauthorizedError(message=translations.get('auth', {}).get('invalid_credentials', 'Невірні дані для входу'))
            
        if check_password_hash(user.password, auth.get('password')):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            if logger:
                logger.info(f"Користувач увійшов: {user.email}")
            
            return jsonify({
                'message': translations.get('auth', {}).get('login_success', 'Успішний вхід'),
                'token': token,
                'user_id': user.id,
                'email': user.email
            })
        
        if logger:
            logger.warning(f"Спроба входу з невірним паролем для користувача: {user.email}")
        raise UnauthorizedError(message=translations.get('auth', {}).get('invalid_credentials', 'Невірні дані для входу'))
    
    return login_route

def token_required(f):
    """
    Декоратор для перевірки токена.
    
    Args:
        f: Функція, яку потрібно декорувати
        
    Returns:
        function: Декорована функція
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        lang = request.args.get('lang', 'uk')
        translations = load_translations(lang)
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            raise UnauthorizedError(message=translations.get('auth', {}).get('token_missing', 'Токен відсутній'))
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            # Використовуємо імпортовану модель User замість отримання з глобального контексту
            current_user = User.query.filter_by(id=data['user_id']).first()
            
            if not current_user:
                raise UnauthorizedError(message=translations.get('auth', {}).get('user_not_found', 'Користувача не знайдено'))
            
            # Додаємо користувача до глобального контексту
            g.current_user = current_user
            
            return f(current_user=current_user, lang=lang, translations=translations, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError(message=translations.get('auth', {}).get('token_expired', 'Токен застарів'))
        except jwt.InvalidTokenError:
            raise UnauthorizedError(message=translations.get('auth', {}).get('token_invalid', 'Невірний токен'))
        
    return decorated 