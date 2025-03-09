"""
Маршрути для роботи з підписками.
"""

import datetime
from flask import request, jsonify

from utils.i18n import load_translations
from utils.error_handler import ValidationError, BadRequestError, handle_database_error

def check_subscription(app, db, User, logger=None):
    """
    Функція для перевірки статусу підписки користувача.
    
    Args:
        app: Екземпляр Flask додатку
        db: Екземпляр бази даних
        User: Модель користувача
        logger: Логер для запису подій
        
    Returns:
        function: Функція-обробник маршруту /check-subscription
    """
    def check_subscription_route(current_user=None, lang='uk', translations=None, *args, **kwargs):
        if not translations:
            translations = load_translations(lang)
        
        try:
            # Перевірка чи активна підписка
            is_active = False
            if current_user.subscription_type == 'premium':
                if current_user.subscription_end and current_user.subscription_end > datetime.datetime.utcnow():
                    is_active = True
                else:
                    # Якщо термін підписки закінчився, змінюємо тип на безкоштовний
                    if logger:
                        logger.info(f"Підписка користувача {current_user.email} закінчилася, змінюємо на безкоштовну")
                    current_user.subscription_type = 'free'
                    current_user.subscription_end = None
                    db.session.commit()
            else:
                is_active = True  # Безкоштовна підписка завжди активна
            
            if logger:
                logger.info(f"Перевірка підписки для користувача {current_user.email}: тип={current_user.subscription_type}, активна={is_active}")
            
            return jsonify({
                'subscription_type': current_user.subscription_type,
                'is_active': is_active,
                'subscription_end': current_user.subscription_end.isoformat() if current_user.subscription_end else None
            }), 200
        except Exception as e:
            if logger:
                logger.error(f"Помилка при перевірці підписки для користувача {current_user.email}: {str(e)}")
            handle_database_error(e, {'user_id': current_user.id, 'email': current_user.email})

    return check_subscription_route

def update_subscription(app, db, User, Payment, logger=None):
    """
    Функція для оновлення підписки користувача.
    
    Args:
        app: Екземпляр Flask додатку
        db: Екземпляр бази даних
        User: Модель користувача
        Payment: Модель платежу
        logger: Логер для запису подій
        
    Returns:
        function: Функція-обробник маршруту /update-subscription
    """
    def update_subscription_route(current_user=None, lang='uk', translations=None, *args, **kwargs):
        if not translations:
            translations = load_translations(lang)
        
        data = request.get_json()
        
        if not data:
            if logger:
                logger.warning(f"Спроба оновлення підписки з невірним запитом для користувача {current_user.email}")
            raise ValidationError(message=translations.get('subscription', {}).get('invalid_request', 'Невірний запит'))
        
        subscription_type = data.get('subscription_type')
        duration = data.get('duration', 30)  # За замовчуванням 30 днів
        payment_id = data.get('payment_id')
        
        if not subscription_type:
            if logger:
                logger.warning(f"Спроба оновлення підписки без вказання типу для користувача {current_user.email}")
            raise ValidationError(message=translations.get('subscription', {}).get('missing_subscription_type', 'Не вказано тип підписки'))
        
        if subscription_type not in ['free', 'premium']:
            if logger:
                logger.warning(f"Спроба оновлення підписки з невірним типом '{subscription_type}' для користувача {current_user.email}")
            raise ValidationError(message=translations.get('subscription', {}).get('invalid_subscription_type', 'Невірний тип підписки'))
        
        try:
            # Оновлення підписки
            current_user.subscription_type = subscription_type
            
            if subscription_type == 'premium':
                current_user.subscription_end = datetime.datetime.utcnow() + datetime.timedelta(days=duration)
                
                # Створення запису про платіж, якщо вказано payment_id
                if payment_id:
                    payment = Payment(
                        user_id=current_user.id,
                        payment_id=payment_id,
                        amount=data.get('amount', 0),
                        currency=data.get('currency', 'USD'),
                        status='completed',
                        created_at=datetime.datetime.utcnow()
                    )
                    db.session.add(payment)
            else:
                current_user.subscription_end = None
            
            db.session.commit()
            
            if logger:
                logger.info(f"Підписка оновлена для користувача {current_user.email}: тип={subscription_type}, тривалість={duration} днів")
            
            return jsonify({
                'message': translations.get('subscription', {}).get('subscription_updated', 'Підписка успішно оновлена'),
                'subscription_type': current_user.subscription_type,
                'is_active': True,
                'subscription_end': current_user.subscription_end.isoformat() if current_user.subscription_end else None
            }), 200
        except Exception as e:
            db.session.rollback()
            if logger:
                logger.error(f"Помилка при оновленні підписки для користувача {current_user.email}: {str(e)}")
            handle_database_error(e, {'user_id': current_user.id, 'email': current_user.email})

    return update_subscription_route

def check_payment(app, db, User, Payment, logger=None):
    """
    Функція для перевірки статусу платежу.
    
    Args:
        app: Екземпляр Flask додатку
        db: Екземпляр бази даних
        User: Модель користувача
        Payment: Модель платежу
        logger: Логер для запису подій
        
    Returns:
        function: Функція-обробник маршруту /check-payment
    """
    def check_payment_route(payment_id, current_user=None, lang='uk', translations=None, *args, **kwargs):
        if not translations:
            translations = load_translations(lang)
        
        try:
            payment = Payment.query.filter_by(payment_id=payment_id).first()
            
            if not payment:
                if logger:
                    logger.warning(f"Спроба перевірки неіснуючого платежу: {payment_id}")
                raise ValidationError(
                    message=translations.get('subscription', {}).get('payment_not_found', 'Платіж не знайдено'),
                    status_code=404
                )
            
            # Якщо користувач вказаний, перевіряємо, чи платіж належить цьому користувачу
            if current_user and payment.user_id != current_user.id:
                if logger:
                    logger.warning(f"Спроба перевірки платежу іншого користувача: {payment_id} (користувач {current_user.email})")
                raise BadRequestError(message=translations.get('subscription', {}).get('payment_not_yours', 'Цей платіж не належить вам'))
            
            if logger:
                logger.info(f"Перевірка платежу {payment_id}: статус={payment.status}")
            
            return jsonify({
                'payment_id': payment.payment_id,
                'status': payment.status,
                'amount': payment.amount,
                'currency': payment.currency,
                'created_at': payment.created_at.isoformat()
            }), 200
        except ValidationError:
            raise
        except Exception as e:
            if logger:
                logger.error(f"Помилка при перевірці платежу {payment_id}: {str(e)}")
            handle_database_error(e, {'payment_id': payment_id})

    return check_payment_route 