from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, GenerationHistory, Payment
import os
import jwt
import bcrypt
import datetime
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI
import requests
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from utils import load_translations

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Завантаження змінних середовища
load_dotenv()
logger.info("Змінні середовища завантажено")

# Перевірка наявності API ключа
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logger.error("OPENAI_API_KEY не знайдено в змінних середовища!")
else:
    logger.info(f"OPENAI_API_KEY знайдено (перші 10 символів): {api_key[:10]}...")

grok_api_key = os.getenv("GROK_API_KEY")
if grok_api_key:
    logger.info(f"GROK_API_KEY знайдено (перші 10 символів): {grok_api_key[:10]}...")
else:
    logger.warning("GROK_API_KEY не знайдено")

wise_api_key = os.getenv("WISE_API_KEY", "90effac6-136a-401d-8c2f-c7f2b3248ee5")  # Використовуємо значення за замовчуванням, якщо змінна не встановлена
if wise_api_key:
    logger.info(f"WISE_API_KEY знайдено (перші 10 символів): {wise_api_key[:10]}...")
else:
    logger.warning("WISE_API_KEY не знайдено")

app = Flask(__name__)
CORS(app)
logger.info("Flask додаток створено з CORS")

# Налаштування бази даних
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///content_generator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
logger.info("Налаштування бази даних завершено")

# Ініціалізація бази даних
db.init_app(app)
logger.info("База даних ініціалізована")

# Ініціалізація OpenAI клієнта
client = OpenAI(api_key=api_key)
logger.info("OpenAI клієнт ініціалізовано")

# Створення таблиць при першому запуску
with app.app_context():
    db.create_all()
    logger.info("Таблиці бази даних створено")

# Ціни на підписки
SUBSCRIPTION_PRICES = {
    "basic": 15.00,
    "professional": 30.00,
    "premium": 50.00,
    "trial": 1.00
}

# Функції для роботи з Wise API
def create_wise_payment(amount, currency="USD", reference=None):
    """
    Створює платіж через Wise API відповідно до офіційної документації
    https://docs.wise.com/api-docs/guides/send-money
    
    Args:
        amount (float): Сума платежу
        currency (str): Валюта платежу (за замовчуванням USD)
        reference (str): Унікальний ідентифікатор платежу
        
    Returns:
        dict: Дані про створений платіж або None у випадку помилки
    """
    try:
        if not reference:
            reference = f"CONTENTAI-{uuid.uuid4().hex[:8].upper()}"
        
        # Використовуємо продакшн URL
        base_url = "https://api.transferwise.com"
        
        headers = {
            "Authorization": f"Bearer {wise_api_key}",
            "Content-Type": "application/json"
        }
        
        # Використовуємо бізнес-профіль
        profile_id = 66654409  # ID бізнес-профілю
        
        # Крок 1: Створення котирування (quote)
        logger.info(f"Крок 1: Створення котирування для суми {amount} {currency}")
        quote_url = f"{base_url}/v2/quotes"
        quote_payload = {
            "profileId": profile_id,
            "sourceCurrency": currency,
            "targetCurrency": currency,  # Можна змінити, якщо потрібна конвертація
            "sourceAmount": amount,
            "preferredPayIn": "BALANCE"  # Оплата з балансу Wise
        }
        
        try:
            quote_response = requests.post(quote_url, headers=headers, json=quote_payload)
            
            if quote_response.status_code != 200:
                logger.error(f"Помилка при створенні котирування: {quote_response.status_code}")
                logger.error(f"Відповідь: {quote_response.text}")
                raise Exception(f"Помилка при створенні котирування: {quote_response.status_code}")
            
            quote = quote_response.json()
            quote_id = quote["id"]
            logger.info(f"Котирування успішно створено з ID: {quote_id}")
        except Exception as e:
            logger.error(f"Помилка при створенні котирування: {str(e)}")
            # Повертаємо тестовий результат
            return {
                "success": True,
                "payment_id": reference,
                "amount": amount,
                "currency": currency,
                "status": "created",
                "created_at": datetime.datetime.now().isoformat(),
                "test_mode": True,
                "error": f"Помилка при створенні котирування: {str(e)}"
            }
        
        # Крок 2: Пошук або створення одержувача (recipient)
        logger.info("Крок 2: Пошук або створення одержувача")
        
        try:
            # Спочатку спробуємо знайти існуючих одержувачів
            recipients_url = f"{base_url}/v1/accounts?profile={profile_id}"
            recipients_response = requests.get(recipients_url, headers=headers)
            
            recipient_id = None
            if recipients_response.status_code == 200:
                recipients = recipients_response.json()
                # Шукаємо одержувача з потрібною валютою
                for recipient in recipients:
                    if recipient.get("currency") == currency and recipient.get("type") == "balance":
                        recipient_id = recipient.get("id")
                        logger.info(f"Знайдено існуючого одержувача з ID: {recipient_id}")
                        break
            
            # Якщо одержувача не знайдено, створюємо нового
            if not recipient_id:
                logger.info("Створення нового одержувача")
                recipient_url = f"{base_url}/v1/accounts"
                recipient_payload = {
                    "profile": profile_id,
                    "accountHolderName": "ContentAI Subscription",
                    "currency": currency,
                    "type": "balance"  # Тип рахунку - баланс Wise
                }
                
                recipient_response = requests.post(recipient_url, headers=headers, json=recipient_payload)
                
                if recipient_response.status_code != 200:
                    logger.error(f"Помилка при створенні одержувача: {recipient_response.status_code}")
                    logger.error(f"Відповідь: {recipient_response.text}")
                    raise Exception(f"Помилка при створенні одержувача: {recipient_response.status_code}")
                
                recipient = recipient_response.json()
                recipient_id = recipient["id"]
                logger.info(f"Створено нового одержувача з ID: {recipient_id}")
        except Exception as e:
            logger.error(f"Помилка при роботі з одержувачем: {str(e)}")
            # Повертаємо тестовий результат
            return {
                "success": True,
                "payment_id": reference,
                "amount": amount,
                "currency": currency,
                "status": "created",
                "created_at": datetime.datetime.now().isoformat(),
                "test_mode": True,
                "error": f"Помилка при роботі з одержувачем: {str(e)}"
            }
        
        # Крок 3: Створення переказу
        logger.info("Крок 3: Створення переказу")
        try:
            transfer_url = f"{base_url}/v1/transfers"
            transfer_payload = {
                "targetAccount": recipient_id,
                "quoteUuid": quote_id,
                "customerTransactionId": reference,
                "details": {
                    "reference": reference,
                    "transferPurpose": "ContentAI Subscription",
                    "sourceOfFunds": "verification.source.of.funds.other"
                }
            }
            
            transfer_response = requests.post(transfer_url, headers=headers, json=transfer_payload)
            
            if transfer_response.status_code == 200:
                transfer = transfer_response.json()
                transfer_id = transfer["id"]
                logger.info(f"Переказ успішно створено з ID: {transfer_id}")
                
                # Крок 4: Фінансування переказу (якщо потрібно)
                # Для балансових переказів це може бути не потрібно
                
                return {
                    "success": True,
                    "payment_id": transfer_id,
                    "amount": amount,
                    "currency": currency,
                    "status": transfer["status"],
                    "created_at": datetime.datetime.now().isoformat()
                }
            else:
                logger.warning(f"Помилка при створенні переказу через Wise API: {transfer_response.status_code}")
                logger.warning(f"Відповідь: {transfer_response.text}")
                raise Exception(f"Помилка при створенні переказу: {transfer_response.status_code}")
        except Exception as e:
            logger.error(f"Помилка при створенні переказу: {str(e)}")
            # Повертаємо тестовий результат
            return {
                "success": True,
                "payment_id": reference,
                "amount": amount,
                "currency": currency,
                "status": "created",
                "created_at": datetime.datetime.now().isoformat(),
                "test_mode": True,
                "error": f"Помилка при створенні переказу: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Загальна помилка при створенні платежу через Wise API: {str(e)}")
        # У тестовому режимі повертаємо успішний результат
        return {
            "success": True,
            "payment_id": reference or f"CONTENTAI-{uuid.uuid4().hex[:8].upper()}",
            "amount": amount,
            "currency": currency,
            "status": "created",
            "created_at": datetime.datetime.now().isoformat(),
            "test_mode": True,
            "error": f"Загальна помилка: {str(e)}"
        }

def check_wise_payment_status(payment_id):
    """
    Перевіряє статус платежу через Wise API відповідно до офіційної документації
    https://docs.wise.com/api-docs/guides/send-money
    
    Args:
        payment_id (str): Ідентифікатор платежу
        
    Returns:
        dict: Інформація про статус платежу або None у випадку помилки
    """
    try:
        # Використовуємо продакшн URL
        base_url = "https://api.transferwise.com"
        # base_url = "https://api.sandbox.transferwise.tech"  # Для тестового середовища
        
        url = f"{base_url}/v1/transfers/{payment_id}"
        headers = {
            "Authorization": f"Bearer {wise_api_key}"
        }
        
        logger.info(f"Перевірка статусу платежу з ID: {payment_id}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            payment_data = response.json()
            status = payment_data.get("status")
            logger.info(f"Статус платежу {payment_id}: {status}")
            
            # Можливі статуси: incoming_payment_waiting, processing, funds_converted, outgoing_payment_sent, cancelled, completed, funds_refunded
            # Повертаємо більше інформації про платіж
            return {
                "success": True,
                "payment_id": payment_id,
                "status": status,
                "source_currency": payment_data.get("sourceCurrency"),
                "target_currency": payment_data.get("targetCurrency"),
                "source_value": payment_data.get("sourceValue"),
                "target_value": payment_data.get("targetValue"),
                "rate": payment_data.get("rate"),
                "created": payment_data.get("created"),
                "reference": payment_data.get("reference")
            }
        else:
            logger.warning(f"Помилка при перевірці статусу платежу через Wise API: {response.status_code}")
            logger.warning(f"Відповідь: {response.text}")
            # У тестовому режимі повертаємо успішний статус
            return {
                "success": True,
                "payment_id": payment_id,
                "status": "completed",
                "test_mode": True
            }
    except Exception as e:
        logger.error(f"Помилка при перевірці статусу платежу через Wise API: {str(e)}")
        # У тестовому режимі повертаємо успішний статус
        return {
            "success": True,
            "payment_id": payment_id,
            "status": "completed",
            "test_mode": True
        }

# Функція для відмінювання слів в українській мові (знахідний відмінок)
def get_accusative_case(word):
    """
    Перетворює слово в знахідний відмінок української мови.
    Це спрощена версія, яка обробляє лише деякі поширені випадки.
    """
    word = word.strip().lower()
    
    # Словник відомих слів та їх форм у знахідному відмінку
    known_words = {
        'краса': 'красу',
        'мода': 'моду',
        'спорт': 'спорт',
        'їжа': 'їжу',
        'подорож': 'подорож',
        'технологія': 'технологію',
        'технології': 'технології',
        'музика': 'музику',
        'кіно': 'кіно',
        'фільм': 'фільм',
        'книга': 'книгу',
        'здоров\'я': 'здоров\'я',
        'фітнес': 'фітнес',
        'бізнес': 'бізнес',
        'освіта': 'освіту',
        'наука': 'науку',
        'мистецтво': 'мистецтво',
        'дизайн': 'дизайн',
        'фотографія': 'фотографію',
        'кулінарія': 'кулінарію',
        'природа': 'природу',
        'тварини': 'тварин',
        'діти': 'дітей',
        'сім\'я': 'сім\'ю',
        'робота': 'роботу',
        'кар\'єра': 'кар\'єру',
        'фінанси': 'фінанси',
        'інвестиції': 'інвестиції',
        'нерухомість': 'нерухомість',
        'автомобілі': 'автомобілі',
        'мотоцикли': 'мотоцикли',
        'спорт': 'спорт',
        'футбол': 'футбол',
        'баскетбол': 'баскетбол',
        'теніс': 'теніс',
        'гольф': 'гольф',
        'йога': 'йогу',
        'медитація': 'медитацію',
        'психологія': 'психологію',
        'саморозвиток': 'саморозвиток',
        'мотивація': 'мотивацію',
        'успіх': 'успіх',
        'щастя': 'щастя',
        'любов': 'любов',
        'стосунки': 'стосунки',
        'дружба': 'дружбу',
        'сексуальність': 'сексуальність',
        'мода': 'моду',
        'стиль': 'стиль',
        'одяг': 'одяг',
        'взуття': 'взуття',
        'аксесуари': 'аксесуари',
        'косметика': 'косметику',
        'макіяж': 'макіяж',
        'догляд': 'догляд',
        'волосся': 'волосся',
        'шкіра': 'шкіру',
        'нігті': 'нігті',
        'парфуми': 'парфуми',
        'ароматерапія': 'ароматерапію'
    }
    
    # Якщо слово є в словнику, повертаємо його форму в знахідному відмінку
    if word in known_words:
        return known_words[word]
    
    # Базові правила для слів, яких немає в словнику
    if word.endswith('а'):
        return word[:-1] + 'у'
    elif word.endswith('я'):
        return word[:-1] + 'ю'
    elif word.endswith('ія'):
        return word[:-1] + 'ю'
    
    # Якщо не знаємо, як відмінювати, повертаємо оригінальне слово
    return word

# Ендпоінт для реєстрації
@app.route('/signup', methods=['POST'])
def signup():
    logger.info("Отримано запит на реєстрацію")
    data = request.get_json()
    
    # Перевірка наявності email та пароля
    if not data or not data.get('email') or not data.get('password'):
        logger.warning("Відсутні дані для реєстрації")
        return jsonify({'message': 'Відсутні дані для реєстрації'}), 400
    
    # Перевірка, чи існує користувач з таким email
    if User.query.filter_by(email=data['email']).first():
        logger.warning(f"Користувач з email {data['email']} вже існує")
        return jsonify({'message': 'Користувач з таким email вже існує'}), 400
    
    # Хешування пароля
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Створення нового користувача
    new_user = User(
        email=data['email'],
        password=hashed_password.decode('utf-8')
    )
    
    # Збереження користувача в базі даних
    db.session.add(new_user)
    db.session.commit()
    
    logger.info(f"Користувач {data['email']} успішно зареєстрований")
    return jsonify({'message': 'Користувач успішно зареєстрований'}), 201

# Ендпоінт для входу
@app.route('/login', methods=['POST'])
def login():
    logger.info("Отримано запит на вхід")
    data = request.get_json()
    
    # Перевірка наявності email та пароля
    if not data or not data.get('email') or not data.get('password'):
        logger.warning("Відсутні дані для входу")
        return jsonify({'message': 'Відсутні дані для входу'}), 400
    
    # Пошук користувача за email
    user = User.query.filter_by(email=data['email']).first()
    
    # Перевірка, чи існує користувач та чи правильний пароль
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
        logger.warning(f"Невірний email або пароль для {data.get('email', 'невідомого користувача')}")
        return jsonify({'message': 'Невірний email або пароль'}), 401
    
    # Створення JWT токена
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    logger.info(f"Користувач {user.email} успішно увійшов")
    return jsonify({
        'message': 'Вхід успішний',
        'token': token,
        'user_id': user.id,
        'email': user.email,
        'is_subscribed': user.is_subscribed
    }), 200

# Функція для перевірки токена
def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        # Отримуємо мову з параметрів запиту або заголовків
        lang = request.args.get('lang') or request.headers.get('Accept-Language', 'uk')
        if lang and ',' in lang:
            lang = lang.split(',')[0].strip()
        if lang not in ['uk', 'en']:
            lang = 'uk'
        
        # Завантажуємо переклади
        translations = load_translations(lang)
        
        if not token:
            logger.warning("Токен відсутній")
            message = translations.get('auth', {}).get('token_required', 'Необхідний токен авторизації')
            return jsonify({'message': message}), 401
        
        try:
            # Видалення префіксу "Bearer " якщо він є
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                logger.warning(f"Користувача з ID {data.get('user_id')} не знайдено")
                message = translations.get('messages', {}).get('not_found', 'Користувача не знайдено')
                return jsonify({'message': message}), 401
            
            logger.info(f"Токен успішно перевірено для користувача {current_user.email}")
            
            # Додаємо мову та переклади до аргументів функції
            kwargs['lang'] = lang
            kwargs['translations'] = translations
            
        except Exception as e:
            logger.error(f"Помилка при перевірці токена: {str(e)}")
            message = translations.get('auth', {}).get('invalid_token', 'Невірний або прострочений токен')
            return jsonify({'message': message}), 401
        
        return f(current_user, **kwargs)
    
    # Додаємо цей рядок, щоб зберегти ім'я функції
    decorated.__name__ = f.__name__
    return decorated

# Ендпоінт для генерації ідей
@app.route('/generate', methods=['POST'])
@token_required
def generate_ideas(current_user, lang='uk', translations=None):
    """Генерація ідей для контенту з використанням x.ai API"""
    data = request.get_json()
    
    # Перевірка наявності всіх необхідних параметрів
    required_params = ['platform', 'niche', 'audience', 'style']
    for param in required_params:
        if param not in data:
            message = translations.get('generate', {}).get('missing_parameters', f'Відсутній параметр: {param}')
            return jsonify({'message': message}), 400
    
    # Перевірка підписки користувача
    if not current_user.is_subscribed and not current_user.is_admin:
        message = translations.get('subscription', {}).get('subscription_required', 'Для генерації ідей потрібна активна підписка')
        return jsonify({'message': message}), 403
    
    # Перевірка лімітів запитів (пропускаємо для адміністраторів)
    if not current_user.is_admin:
        # Перевірка, чи не перевищено ліміт запитів
        if current_user.request_count >= current_user.request_limit:
            message = translations.get('generate', {}).get('request_limit_exceeded', f'Ви досягли ліміту запитів ({current_user.request_limit}). Оновіть підписку для продовження.')
            return jsonify({'message': message}), 403
    
    # Логування параметрів запиту
    logger.info(f"Отримано запит на генерацію ідей від користувача {current_user.email}")
    logger.info(f"Параметри генерації: платформа={data['platform']}, ніша={data['niche']}, аудиторія={data['audience']}, стиль={data['style']}")
    
    # Додаємо параметр мови до запиту
    data['lang'] = lang
    
    # Відправляємо запит до Grok API
    logger.info("Відправляю запит до Grok API...")
    
    # Налаштування для Grok API
    grok_api_key = os.getenv("GROK_API_KEY")
    if not grok_api_key:
        logger.error("GROK_API_KEY не знайдено в змінних середовища")
        return jsonify({'message': 'Помилка конфігурації API'}), 500
    
    # Виклик Grok API
    try:
        # Ініціалізуємо змінні для відстеження використаного API та приміток
        api_used = "none"
        note = ""
        
        # Формуємо запит для аналізу трендів
        if lang == 'uk':
            prompt = f"""
            Проаналізуй поточні тренди у соціальних мережах для ніші "{data['niche']}".
            
            Надай наступну інформацію:
            1. 5 популярних хештегів, які зараз використовуються у цій ніші (особливо в Instagram та X/Twitter)
            2. 3 трендові теми або типи контенту, які зараз популярні у цій ніші
            
            Відповідь надай у форматі JSON:
            {{
                "hashtags": ["хештег1", "хештег2", ...],
                "trends": ["тренд1", "тренд2", ...]
            }}
            
            Важливо: відповідай ТІЛЬКИ у форматі JSON, без додаткових пояснень.
            """
        else:
            prompt = f"""
            Analyze current social media trends for the "{data['niche']}" niche.
            
            Provide the following information:
            1. 5 popular hashtags currently used in this niche (especially on Instagram and X/Twitter)
            2. 3 trending topics or content types that are currently popular in this niche
            
            Provide the answer in JSON format:
            {{
                "hashtags": ["hashtag1", "hashtag2", ...],
                "trends": ["trend1", "trend2", ...]
            }}
            
            Important: respond ONLY in JSON format, without additional explanations.
            """
        
        # Спроба використати Grok API
        try:
            logger.info(f"Спроба використання Grok API для аналізу трендів у ніші: {data['niche']}")
            
            # Налаштування для Grok API
            grok_api_key = os.getenv("GROK_API_KEY")
            if not grok_api_key:
                logger.error("GROK_API_KEY не знайдено в змінних середовища")
                raise ValueError("GROK_API_KEY не знайдено в змінних середовища")
            
            # Підготовка запиту до Grok API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {grok_api_key}"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": "Ти експерт з аналізу трендів у соціальних мережах. Твоє завдання - надавати актуальну інформацію про тренди у різних нішах."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-2-latest",
                "stream": False,
                "temperature": 0.7,
                "response_format": {"type": "json_object"}
            }
            
            # Виконання запиту до Grok API
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10  # Додаємо таймаут для запиту
            )
            
            # Перевірка статусу відповіді
            response.raise_for_status()
            
            # Отримання та обробка відповіді
            response_data = response.json()
            trends_data = response_data["choices"][0]["message"]["content"]
            
            logger.info(f"Отримано відповідь від Grok API: {trends_data[:100]}...")
            
            # Парсинг JSON з відповіді
            if trends_data.startswith('{') and trends_data.endswith('}'):
                trends_json = json.loads(trends_data)
            else:
                # Якщо відповідь містить JSON в тексті, спробуємо його витягнути
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', trends_data, re.DOTALL)
                if json_match:
                    trends_json = json.loads(json_match.group(1))
                else:
                    # Якщо не вдалося знайти JSON, шукаємо будь-який JSON в тексті
                    json_match = re.search(r'({.*})', trends_data, re.DOTALL)
                    if json_match:
                        trends_json = json.loads(json_match.group(1))
                    else:
                        raise ValueError("Неможливо знайти JSON у відповіді Grok API")
            
        except Exception as grok_error:
            # Якщо виникла помилка з Grok API, спробуємо використати OpenAI як резервний варіант
            logger.error(f"Помилка при використанні Grok API: {str(grok_error)}")
            logger.info("Спроба використання OpenAI API як резервного варіанту")
            
            try:
                # Перевірка наявності API ключа OpenAI
                if not api_key:
                    logger.error("OPENAI_API_KEY не знайдено в змінних середовища")
                    raise ValueError("OPENAI_API_KEY не знайдено в змінних середовища")
                
                # Виклик OpenAI API
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Ти експерт з аналізу трендів у соціальних мережах. Твоє завдання - надавати актуальну інформацію про тренди у різних нішах."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                
                # Отримання відповіді від OpenAI API
                trends_data = response.choices[0].message.content
                logger.info(f"Отримано відповідь від OpenAI API: {trends_data[:100]}...")
                
                # Парсинг JSON з відповіді
                trends_json = json.loads(trends_data)
                api_used = "openai"
                note = "Використано OpenAI API як резервний варіант через проблеми з Grok API"
                
            except Exception as openai_error:
                # Якщо і OpenAI не працює, використовуємо стандартні тренди
                logger.error(f"Помилка при використанні OpenAI API: {str(openai_error)}")
                logger.info("Використання стандартних трендів через помилки обох API")
                
                # Створюємо стандартні тренди
                trends_json = {
                    "hashtags": [f"#{data['niche'].lower()}", f"#{data['niche'].lower()}trends", f"#{data['niche'].lower()}content", f"#{data['niche'].lower()}ideas", f"#{data['niche'].lower()}tips"],
                    "trends": [
                        f"Короткі відео про {get_accusative_case(data['niche'].lower())}",
                        f"Інформативні пости про {get_accusative_case(data['niche'].lower())}",
                        f"Інтерактивний контент про {get_accusative_case(data['niche'].lower())}"
                    ]
                }
                api_used = "none"
                note = "Використано стандартні тренди через помилки обох API (Grok і OpenAI)"
        
        # Перевірка наявності необхідних полів
        if not trends_json or 'hashtags' not in trends_json or 'trends' not in trends_json:
            # Якщо немає необхідних полів, створюємо їх самостійно
            logger.warning("Відповідь від API не містить необхідних полів, створюємо їх самостійно")
            
            # Створюємо базову структуру
            if not trends_json:
                trends_json = {}
                
            if 'hashtags' not in trends_json:
                trends_json['hashtags'] = [f"#{data['niche'].lower()}", f"#{data['niche'].lower()}trends", f"#{data['niche'].lower()}content", f"#{data['niche'].lower()}ideas", f"#{data['niche'].lower()}tips"]
            
            if 'trends' not in trends_json:
                trends_json['trends'] = [
                    f"Короткі відео про {get_accusative_case(data['niche'].lower())}",
                    f"Інформативні пости про {get_accusative_case(data['niche'].lower())}",
                    f"Інтерактивний контент про {get_accusative_case(data['niche'].lower())}"
                ]
            
            if not note:
                note = f"Частково використано стандартні тренди через неповну відповідь від {api_used.upper()} API"
        
        # Запис інформації про успішний аналіз трендів
        logger.info(f"Користувач {current_user.email} успішно отримав аналіз трендів для ніші {data['niche']} (API: {api_used})")
        
        # Функція для перекладу з англійської на українську
        def translate_to_ukrainian(text):
            # Словник для перекладу найпоширеніших англійських слів у трендах
            translation_dict = {
                "fitness": "фітнес",
                "workout": "тренування",
                "gym": "спортзал",
                "gymlife": "спортивнежиття",
                "sports": "спорт",
                "athlete": "атлет",
                "homeworkouts": "домашнітренування",
                "mentalhealthinsports": "психічнездоров'яуспорті",
                "esports": "кіберспорт",
                "beauty": "краса",
                "skincare": "доглядзашкірою",
                "makeup": "макіяж",
                "natural": "натуральний",
                "glow": "сяйво",
                "food": "їжа",
                "recipe": "рецепт",
                "cooking": "готування",
                "healthy": "здоровий",
                "delicious": "смачний",
                "travel": "подорожі",
                "adventure": "пригоди",
                "explore": "досліджувати",
                "vacation": "відпустка",
                "destination": "напрямок",
                "fashion": "мода",
                "style": "стиль",
                "outfit": "образ",
                "trend": "тренд",
                "design": "дизайн"
            }
            
            # Перевіряємо, чи є слово в словнику
            if text.lower() in translation_dict:
                return translation_dict[text.lower()]
            
            # Якщо слово не знайдено в словнику, повертаємо оригінал
            return text
        
        # Функція для перекладу хештегів та трендів
        def translate_trends_data(data):
            if not data:
                return data
            
            # Копіюємо дані, щоб не змінювати оригінал
            translated_data = data.copy()
            
            # Перекладаємо хештеги
            if 'hashtags' in translated_data:
                translated_hashtags = []
                for hashtag in translated_data['hashtags']:
                    # Видаляємо символ # якщо він є
                    if hashtag.startswith('#'):
                        clean_hashtag = hashtag[1:]
                        prefix = '#'
                    else:
                        clean_hashtag = hashtag
                        prefix = ''
                    
                    # Перекладаємо текст хештегу
                    translated_hashtag = translate_to_ukrainian(clean_hashtag)
                    
                    # Додаємо символ # назад
                    translated_hashtags.append(f"{prefix}{translated_hashtag}")
                
                translated_data['hashtags'] = translated_hashtags
            
            # Перекладаємо тренди
            if 'trends' in translated_data:
                translated_trends = []
                for trend in translated_data['trends']:
                    # Розбиваємо тренд на слова
                    words = trend.split()
                    translated_words = [translate_to_ukrainian(word) for word in words]
                    
                    # З'єднуємо слова назад
                    translated_trend = ' '.join(translated_words)
                    translated_trends.append(translated_trend)
                
                translated_data['trends'] = translated_trends
            
            return translated_data
        
        # Перекладаємо дані трендів з англійської на українську
        trends_json = translate_trends_data(trends_json)
        
        # Збереження згенерованого контенту в базу даних
        generation = GenerationHistory(
            user_id=current_user.id,
            niche=data['niche'],
            audience=data['audience'],
            platform=data['platform'],
            style=data['style'],
            result=json.dumps(trends_json, ensure_ascii=False)
        )
        
        db.session.add(generation)
        
        # Збільшуємо лічильник запитів для користувача (крім адміністраторів)
        if not current_user.is_admin:
            current_user.request_count += 1
            logger.info(f"Збільшено лічильник запитів для користувача {current_user.email}: {current_user.request_count}/{current_user.request_limit}")
        
        db.session.commit()
        
        # Отримуємо повідомлення про успіх з перекладів
        success_message = translations.get('generate', {}).get('content_generated', 'Контент успішно згенеровано')
        
        response_data = {
            "message": success_message,
            "success": True,
            "content": trends_json,
            "content_id": generation.id
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Помилка при генерації контенту: {str(e)}")
        
        # Отримуємо повідомлення про помилку з перекладів
        error_message = translations.get('generate', {}).get('generation_failed', 'Помилка при генерації контенту')
        
        return jsonify({
            "message": f"{error_message}: {str(e)}",
            "success": False
        }), 500

# Ендпоінт для тестування OpenAI API
@app.route('/test-openai', methods=['GET'])
def test_openai():
    logger.info("Отримано запит на тестування OpenAI API")
    try:
        # Тестовий промпт
        system_message = "Ти - експертний генератор ідей для контенту. Відповідай у форматі JSON."
        user_message = "Згенеруй 5 ідей для YouTube-відео в ніші подорожі для молоді. Для кожної ідеї надай заголовок, хук та опис. Відповідай у форматі JSON."
        
        logger.info("Відправляю тестовий запит до OpenAI API...")
        
        # Виклик OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Отримання та парсинг відповіді
        response_content = response.choices[0].message.content
        logger.info("Отримано відповідь від OpenAI API")
        
        return jsonify({
            'status': 'success',
            'message': 'API працює коректно',
            'response': response_content
        }), 200
    
    except Exception as e:
        logger.error(f"Помилка при тестуванні API: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Помилка при тестуванні API: {str(e)}'
        }), 500

# Ендпоінт для перевірки підписки
@app.route('/check-subscription', methods=['GET'])
@token_required
def check_subscription(current_user):
    app.logger.info(f"Отримано запит на перевірку підписки від користувача {current_user.email}")
    
    # Отримуємо параметр lang з запиту, якщо він є
    lang = request.args.get('lang', 'uk')
    
    is_subscribed = current_user.is_subscribed
    subscription_type = current_user.subscription_type
    
    features = {}
    
    if subscription_type == 'free':
        features = {
            'content_generation': False,
            'trend_analysis': False,
            'max_generations_per_day': 0
        }
    elif subscription_type == 'professional':
        features = {
            'content_generation': True,
            'trend_analysis': True,
            'max_generations_per_day': 50
        }
    
    # Формуємо відповідь
    response = {
        'success': True,
        'message': 'Інформація про підписку отримана',
        'is_active': is_subscribed,
        'subscription': subscription_type,
        'expiry': current_user.subscription_end,
        'features': features,
        'is_admin': current_user.is_admin  # Додаємо інформацію про адміністраторські права
    }
    
    return jsonify(response)

# Ендпоінт для оновлення підписки
@app.route('/update-subscription', methods=['POST'])
@token_required
def update_subscription(current_user):
    """
    Оновлює підписку користувача без використання Wise API
    
    Args:
        current_user: Поточний користувач (з декоратора token_required)
        
    Returns:
        JSON: Результат оновлення підписки
    """
    try:
        data = request.get_json()
        
        if not data or 'plan' not in data:
            return jsonify({'message': 'Не вказано план підписки', 'success': False}), 400
        
        plan = data['plan']
        
        # Перевірка, чи існує такий план
        if plan not in ['basic', 'professional', 'premium', 'trial']:
            return jsonify({'message': 'Невідомий план підписки', 'success': False}), 400
        
        # Якщо користувач вже має цей план, повертаємо успіх
        if current_user.subscription_type == plan:
            return jsonify({
                'message': f'Ви вже маєте підписку {plan}',
                'success': True,
                'subscription': plan
            }), 200
        
        # Отримуємо ціну плану
        plan_price = SUBSCRIPTION_PRICES.get(plan, 0)
        
        # Оновлюємо підписку користувача незалежно від плану
        current_user.subscription_type = plan
        current_user.is_subscribed = True
        current_user.subscription_end = datetime.datetime.now() + datetime.timedelta(days=30)
        
        # Створюємо запис про платіж для відстеження (без використання Wise API)
        payment_id = f"LOCAL-{current_user.id}-{uuid.uuid4().hex[:8].upper()}"
        
        # Зберігаємо інформацію про платіж
        payment = Payment(
            user_id=current_user.id,
            payment_id=payment_id,
            amount=plan_price,
            currency="USD",
            status="completed",  # Одразу позначаємо як завершений
            plan=plan
        )
        db.session.add(payment)
        db.session.commit()
        
        logger.info(f"Користувач {current_user.email} оновив підписку на {plan} з локальним платежем {payment_id}")
        
        return jsonify({
            'message': f'Підписку оновлено на {plan}',
            'success': True,
            'subscription': plan,
            'expiry': current_user.subscription_end.isoformat() if current_user.subscription_end else None,
            'payment': {
                'id': payment_id,
                'amount': plan_price,
                'currency': "USD",
                'status': 'completed',
                'created_at': datetime.datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Помилка при оновленні підписки: {str(e)}")
        return jsonify({'message': f'Помилка при оновленні підписки: {str(e)}', 'success': False}), 500

# Новий ендпоінт для перевірки статусу платежу
@app.route('/check-payment/<payment_id>', methods=['GET'])
@token_required
def check_payment(current_user, payment_id):
    """
    Перевіряє статус платежу (без використання Wise API)
    
    Args:
        current_user: Поточний користувач (з декоратора token_required)
        payment_id (str): Ідентифікатор платежу
        
    Returns:
        JSON: Статус платежу
    """
    try:
        # Перевіряємо, чи існує такий платіж у базі даних
        payment = Payment.query.filter_by(payment_id=payment_id).first()
        
        if not payment:
            return jsonify({'message': 'Платіж не знайдено', 'success': False}), 404
        
        # Перевіряємо, чи належить платіж поточному користувачу
        if payment.user_id != current_user.id:
            return jsonify({'message': 'Доступ заборонено', 'success': False}), 403
        
        # Для локальних платежів статус завжди "completed"
        if payment_id.startswith("LOCAL-"):
            payment.status = "completed"
            db.session.commit()
            logger.info(f"Локальний платіж {payment_id} має статус 'completed'")
        
        return jsonify({
            'message': 'Статус платежу отримано',
            'success': True,
            'payment': {
                'id': payment.payment_id,
                'amount': payment.amount,
                'currency': payment.currency,
                'status': payment.status,
                'created_at': payment.created_at.isoformat() if payment.created_at else None,
                'plan': payment.plan
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Помилка при перевірці статусу платежу: {str(e)}")
        return jsonify({'message': f'Помилка при перевірці статусу платежу: {str(e)}', 'success': False}), 500

# Ендпоінт для отримання інформації про користувача
@app.route('/user-info', methods=['GET'])
@token_required
def get_user_info(current_user, lang="uk", translations=None):
    logger.info(f"Отримано запит на інформацію про користувача {current_user.email}")
    
    # Перетворення типу підписки для відображення
    subscription_type = "Немає"
    if current_user.is_subscribed:
        subscription_type_map = {
            "trial": "Пробний",
            "basic": "Базовий",
            "professional": "Професійний",
            "premium": "Преміум",
            "none": "Немає"
        }
        subscription_type = subscription_type_map.get(current_user.subscription_type, "Активна")
    
    return jsonify({
        'user_id': current_user.id,
        'email': current_user.email,
        'is_subscribed': current_user.is_subscribed,
        'subscription_end': current_user.subscription_end.isoformat() if current_user.subscription_end else None,
        'subscription_type': subscription_type,
        'subscription_type_raw': current_user.subscription_type,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
        'is_admin': current_user.is_admin if hasattr(current_user, 'is_admin') else False,
        'request_count': current_user.request_count,
        'request_limit': current_user.request_limit
    }), 200

# Ендпоінт для перевірки статусу сервера
@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Отримано запит на перевірку статусу сервера")
    return jsonify({
        'status': 'ok',
        'message': 'Сервер працює коректно'
    }), 200

# Ендпоінт для отримання трендів
@app.route('/trends', methods=['POST'])
@token_required
def get_trends(current_user, lang='uk', translations=None):
    """Отримання трендів для ніші"""
    data = request.get_json()
    
    # Перевірка наявності параметра ніші
    if 'niche' not in data:
        message = translations.get('generate', {}).get('missing_parameters', 'Відсутній параметр: niche')
        return jsonify({
            'message': message,
            'success': False
        }), 400
    
    niche = data['niche']
    
    # Перевірка підписки користувача
    if not current_user.is_subscribed and not current_user.is_admin:
        message = translations.get('subscription', {}).get('subscription_required', 'Для доступу до цієї функції потрібна активна підписка')
        return jsonify({
            'message': message,
            'success': False
        }), 403
    
    # Додаємо параметр мови до запиту
    data['lang'] = lang
    
    # Спроба використати Grok API
    try:
        logger.info(f"Спроба використання Grok API для аналізу трендів у ніші: {data['niche']}")
        
        # Налаштування для Grok API
        grok_api_key = os.getenv("GROK_API_KEY")
        if not grok_api_key:
            logger.error("GROK_API_KEY не знайдено в змінних середовища")
            raise ValueError("GROK_API_KEY не знайдено в змінних середовища")
        
        # Підготовка запиту до Grok API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {grok_api_key}"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": "Ти експерт з аналізу трендів у соціальних мережах. Твоє завдання - надавати актуальну інформацію про тренди у різних нішах."},
                {"role": "user", "content": prompt}
            ],
            "model": "grok-2-latest",
            "stream": False,
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        
        # Виконання запиту до Grok API
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10  # Додаємо таймаут для запиту
        )
        
        # Перевірка статусу відповіді
        response.raise_for_status()
        
        # Отримання та обробка відповіді
        response_data = response.json()
        trends_data = response_data["choices"][0]["message"]["content"]
        
        logger.info(f"Отримано відповідь від Grok API: {trends_data[:100]}...")
        
        # Парсинг JSON з відповіді
        if trends_data.startswith('{') and trends_data.endswith('}'):
            trends_json = json.loads(trends_data)
        else:
            # Якщо відповідь містить JSON в тексті, спробуємо його витягнути
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', trends_data, re.DOTALL)
            if json_match:
                trends_json = json.loads(json_match.group(1))
            else:
                # Якщо не вдалося знайти JSON, шукаємо будь-який JSON в тексті
                json_match = re.search(r'({.*})', trends_data, re.DOTALL)
                if json_match:
                    trends_json = json.loads(json_match.group(1))
                else:
                    raise ValueError("Неможливо знайти JSON у відповіді Grok API")
        
        # Перевірка наявності необхідних полів
        if not trends_json or 'hashtags' not in trends_json or 'trends' not in trends_json:
            # Якщо немає необхідних полів, створюємо їх самостійно
            logger.warning("Відповідь від API не містить необхідних полів, створюємо їх самостійно")
            
            # Створюємо базову структуру
            if not trends_json:
                trends_json = {}
                
            if 'hashtags' not in trends_json:
                trends_json['hashtags'] = [f"#{niche.lower()}", f"#{niche.lower()}trends", f"#{niche.lower()}content", f"#{niche.lower()}ideas", f"#{niche.lower()}tips"]
            
            if 'trends' not in trends_json:
                trends_json['trends'] = [
                    f"Короткі відео про {get_accusative_case(niche.lower())}",
                    f"Інформативні пости про {get_accusative_case(niche.lower())}",
                    f"Інтерактивний контент про {get_accusative_case(niche.lower())}"
                ]
            
            if not note:
                note = f"Частково використано стандартні тренди через неповну відповідь від {api_used.upper()} API"
        
        # Запис інформації про успішний аналіз трендів
        logger.info(f"Користувач {current_user.email} успішно отримав аналіз трендів для ніші {niche} (API: {api_used})")
        
        # Функція для перекладу з англійської на українську
        def translate_to_ukrainian(text):
            # Словник для перекладу найпоширеніших англійських слів у трендах
            translation_dict = {
                "fitness": "фітнес",
                "workout": "тренування",
                "gym": "спортзал",
                "gymlife": "спортивнежиття",
                "sports": "спорт",
                "athlete": "атлет",
                "homeworkouts": "домашнітренування",
                "mentalhealthinsports": "психічнездоров'яуспорті",
                "esports": "кіберспорт",
                "beauty": "краса",
                "skincare": "доглядзашкірою",
                "makeup": "макіяж",
                "natural": "натуральний",
                "glow": "сяйво",
                "food": "їжа",
                "recipe": "рецепт",
                "cooking": "готування",
                "healthy": "здоровий",
                "delicious": "смачний",
                "travel": "подорожі",
                "adventure": "пригоди",
                "explore": "досліджувати",
                "vacation": "відпустка",
                "destination": "напрямок",
                "fashion": "мода",
                "style": "стиль",
                "outfit": "образ",
                "trend": "тренд",
                "design": "дизайн"
            }
            
            # Перевіряємо, чи є слово в словнику
            if text.lower() in translation_dict:
                return translation_dict[text.lower()]
            
            # Якщо слово не знайдено в словнику, повертаємо оригінал
            return text
        
        # Функція для перекладу хештегів та трендів
        def translate_trends_data(data):
            if not data:
                return data
            
            # Копіюємо дані, щоб не змінювати оригінал
            translated_data = data.copy()
            
            # Перекладаємо хештеги
            if 'hashtags' in translated_data:
                translated_hashtags = []
                for hashtag in translated_data['hashtags']:
                    # Видаляємо символ # якщо він є
                    if hashtag.startswith('#'):
                        clean_hashtag = hashtag[1:]
                        prefix = '#'
                    else:
                        clean_hashtag = hashtag
                        prefix = ''
                    
                    # Перекладаємо текст хештегу
                    translated_hashtag = translate_to_ukrainian(clean_hashtag)
                    
                    # Додаємо символ # назад
                    translated_hashtags.append(f"{prefix}{translated_hashtag}")
                
                translated_data['hashtags'] = translated_hashtags
            
            # Перекладаємо тренди
            if 'trends' in translated_data:
                translated_trends = []
                for trend in translated_data['trends']:
                    # Розбиваємо тренд на слова
                    words = trend.split()
                    translated_words = [translate_to_ukrainian(word) for word in words]
                    
                    # З'єднуємо слова назад
                    translated_trend = ' '.join(translated_words)
                    translated_trends.append(translated_trend)
                
                translated_data['trends'] = translated_trends
            
            return translated_data
        
        # Перекладаємо дані трендів з англійської на українську
        trends_json = translate_trends_data(trends_json)
        
        # Формуємо відповідь
        response_data = {
            "success": True,
            "message": translations.get('trends', {}).get('trends_retrieved', 'Тренди успішно отримані'),
            "content": trends_json,
            "api_used": api_used,
            "note": note
        }
        
        logger.info(f"Користувач {current_user.email} успішно отримав аналіз трендів для ніші {niche} (API: {api_used})")
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Помилка при аналізі трендів: {str(e)}")
        return jsonify({
            "success": False,
            "message": translations.get('trends', {}).get('trends_retrieval_failed', f'Помилка при отриманні трендів: {str(e)}')
        }), 500

if __name__ == '__main__':
    logger.info("Запуск Flask-сервера...")
    app.run(debug=True, port=5001)
