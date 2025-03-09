from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, GenerationHistory, Payment
import os
import datetime
import json
from dotenv import load_dotenv
from openai import OpenAI
from utils.i18n import load_translations
from utils.logger import app_logger, auth_logger, content_logger, subscription_logger, log_request, log_response, log_exception
from utils.error_handler import register_error_handlers, ValidationError, ExternalServiceError, handle_external_service_error

# Завантаження змінних середовища
load_dotenv()
app_logger.info("Змінні середовища завантажено")

# Перевірка наявності API ключів
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    app_logger.error("OPENAI_API_KEY не знайдено в змінних середовища!")
else:
    app_logger.info(f"OPENAI_API_KEY знайдено (перші 10 символів): {api_key[:10]}...")

grok_api_key = os.getenv("GROK_API_KEY")
if grok_api_key:
    app_logger.info(f"GROK_API_KEY знайдено (перші 10 символів): {grok_api_key[:10]}...")
else:
    app_logger.warning("GROK_API_KEY не знайдено")

wise_api_key = os.getenv("WISE_API_KEY", "90effac6-136a-401d-8c2f-c7f2b3248ee5")
if wise_api_key:
    app_logger.info(f"WISE_API_KEY знайдено (перші 10 символів): {wise_api_key[:10]}...")
else:
    app_logger.warning("WISE_API_KEY не знайдено")

wise_profile_id = os.getenv('WISE_PROFILE_ID')
secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# Ініціалізація клієнта OpenAI
openai_client = OpenAI(api_key=api_key)
app_logger.info("Клієнт OpenAI ініціалізовано")

# Створення екземпляру Flask
app = Flask(__name__)
app_logger.info("Екземпляр Flask створено")

# Налаштування CORS
CORS(app)
app_logger.info("CORS налаштовано")

# Налаштування бази даних
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///content_generator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key
db.init_app(app)
app_logger.info("База даних налаштована")

# Створення таблиць бази даних
with app.app_context():
    db.create_all()
    app_logger.info("Таблиці бази даних створено")

# Реєстрація обробників помилок
register_error_handlers(app)
app_logger.info("Обробники помилок зареєстровано")

# Імпорт маршрутів
from auth.routes import signup, login, token_required
from subscription.routes import check_subscription, update_subscription, check_payment
from content.routes import generate_ideas, get_trends

# Реєстрація ендпоінтів для аутентифікації
signup_route = signup(app, db, User, app_logger)
login_route = login(app, db, User, app_logger)

app.route('/signup', methods=['POST'])(signup_route)
app.route('/login', methods=['POST'])(login_route)

# Реєстрація ендпоінтів для підписки
check_subscription_route = check_subscription(app, db, User, app_logger)
update_subscription_route = update_subscription(app, db, User, Payment, app_logger)
check_payment_route = check_payment(app, db, User, Payment, app_logger)

app.route('/check-subscription', methods=['GET'])(token_required(check_subscription_route))
app.route('/update-subscription', methods=['POST'])(token_required(update_subscription_route))
app.route('/check-payment', methods=['GET'])(token_required(check_payment_route))

# Реєстрація ендпоінтів для генерації контенту
generate_ideas_route = generate_ideas(app, db, User, openai_client, app_logger)
get_trends_route = get_trends(app, db, User, openai_client, app_logger)

app.route('/generate', methods=['POST'])(token_required(generate_ideas_route))
app.route('/trends', methods=['POST'])(token_required(get_trends_route))

# Ендпоінт для перевірки здоров'я сервера
@app.route('/health', methods=['GET'])
def health_check():
    """
    Ендпоінт для перевірки здоров'я сервера.
    """
    app_logger.info("Отримано запит на перевірку здоров'я сервера")
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.datetime.utcnow().isoformat()
    }), 200

# Запуск сервера
if __name__ == '__main__':
    app_logger.info("Запуск сервера на порту 5001")
    app.run(debug=True, port=5001)
