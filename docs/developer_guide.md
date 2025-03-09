# Керівництво для розробників ContentAI

Цей документ містить інструкції для розробників, які працюють з проєктом ContentAI.

## Структура проєкту

Проєкт ContentAI складається з двох основних частин:
- `frontend-app` - фронтенд на базі Next.js
- `backend-api` - бекенд на базі Flask

Детальний опис структури проєкту можна знайти в [документації структури проєкту](./project_structure.md).

## Налаштування середовища розробки

### Фронтенд

1. Встановіть залежності:
   ```bash
   cd frontend-app
   npm install
   ```

2. Запустіть сервер розробки:
   ```bash
   npm run dev
   ```

3. Відкрийте [http://localhost:3000](http://localhost:3000) у браузері.

### Бекенд

1. Створіть віртуальне середовище Python:
   ```bash
   cd backend-api
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate     # для Windows
   ```

2. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```

3. Запустіть сервер розробки:
   ```bash
   python app.py
   ```

4. API буде доступне за адресою [http://localhost:5001](http://localhost:5001).

## Робота з модульною структурою

### Фронтенд

Фронтенд використовує App Router Next.js з підтримкою інтернаціоналізації через параметр `[lang]`.

#### Компоненти

Компоненти організовані за функціональним призначенням:
- `components/ui` - базові UI-компоненти (кнопки, форми, поля вводу)
- `components/layouts` - компоненти макетів
- `components/features` - компоненти для конкретних функцій

Для додавання нового компонента:
1. Визначте, до якої категорії він належить
2. Створіть файл у відповідній директорії
3. Імпортуйте компонент там, де він потрібен

#### Локалізація

Для роботи з локалізацією використовуйте функцію `getDictionary`:

```jsx
// app/[lang]/page.js
import { getDictionary } from './dictionaries'

export default async function Page({ params: { lang } }) {
  const dictionary = await getDictionary(lang, 'auth')  // Завантаження перекладів для модуля auth
  
  return (
    <div>
      <h1>{dictionary.login}</h1>
    </div>
  )
}
```

Для додавання нових перекладів:
1. Додайте ключі та значення у відповідний файл у `public/locales/[lang]/[module]/common.json`
2. Переконайтеся, що ключі однакові для всіх мов

### Бекенд

Бекенд використовує модульну структуру з розділенням на функціональні модулі.

#### Маршрути

Маршрути організовані за функціональним призначенням:
- `auth/routes.py` - маршрути для автентифікації та авторизації
- `subscription/routes.py` - маршрути для роботи з підписками
- `content/routes.py` - маршрути для генерації контенту

Для додавання нового маршруту:
1. Визначте, до якого модуля він належить
2. Додайте функцію в відповідний файл `routes.py`
3. Зареєструйте маршрут у `app.py`

Приклад додавання нового маршруту:

```python
# auth/routes.py
def reset_password(app, db, User):
    @app.route('/reset-password', methods=['POST'])
    def reset_password_route():
        # Логіка скидання пароля
        return jsonify({'message': 'Password reset email sent'})
    
    return reset_password_route

# app.py
from auth.routes import reset_password

# Реєстрація маршруту
reset_password_route = reset_password(app, db, User)
```

#### Моделі

Моделі організовані за функціональним призначенням:
- `models/user/model.py` - модель користувача
- `models/content/model.py` - моделі для контенту
- `models/payment/model.py` - моделі для платежів

Для додавання нової моделі:
1. Визначте, до якого модуля вона належить
2. Створіть файл `model.py` у відповідній директорії
3. Імпортуйте модель у `models/__init__.py`

Приклад додавання нової моделі:

```python
# models/notification/model.py
from .. import db

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

# models/__init__.py
from .notification import Notification

__all__ = ['db', 'User', 'GenerationHistory', 'Payment', 'Notification']
```

#### Локалізація

Для роботи з локалізацією використовуйте функцію `load_translations`:

```python
from utils.i18n import load_translations

@app.route('/api/endpoint', methods=['GET'])
def endpoint():
    lang = request.args.get('lang', 'uk')
    translations = load_translations(lang)
    
    return jsonify({'message': translations['messages']['success']})
```

Для додавання нових перекладів:
1. Додайте ключі та значення у відповідний файл у `locales/[lang].json`
2. Переконайтеся, що ключі однакові для всіх мов

## Тестування

### Запуск тестів

Для запуску всіх тестів використовуйте команду:

```bash
cd backend-api
python -m pytest
```

Для запуску конкретного тесту:

```bash
python -m pytest tests/auth/test_auth.py
```

Для запуску тестів з детальним виводом:

```bash
python -m pytest -v
```

### Модульні тести

Модульні тести знаходяться в директорії `backend-api/tests` і розділені за функціональними модулями:

- `tests/auth/` - тести для модуля автентифікації
- `tests/content/` - тести для модуля генерації контенту
- `tests/subscription/` - тести для модуля підписок
- `tests/utils/` - тести для утиліт

### Інтеграційні тести

Інтеграційні тести знаходяться в директорії `backend-api/tests/integration` і перевіряють взаємодію між різними модулями:

- `tests/integration/test_auth_subscription.py` - тести взаємодії між модулями автентифікації та підписок
- `tests/integration/test_auth_content.py` - тести взаємодії між модулями автентифікації та генерації контенту
- `tests/integration/test_subscription_content.py` - тести взаємодії між модулями підписок та генерації контенту

Для запуску тільки інтеграційних тестів:

```bash
python -m pytest tests/integration/
```

### Утиліти для тестування

Утиліти для тестування знаходяться в файлі `backend-api/tests/integration/test_utils.py` і містять:

- `generate_password_hash()` - функція для генерації хешу пароля для тестів
- `token_required_test()` - декоратор для перевірки токена в тестах
- `register_test_routes()` - функція для реєстрації тестових маршрутів

### Написання нових тестів

При написанні нових тестів дотримуйтесь наступних правил:

1. **Модульні тести** повинні перевіряти функціональність окремих модулів і не повинні залежати від інших модулів.
2. **Інтеграційні тести** повинні перевіряти взаємодію між модулями і використовувати утиліти для тестування.
3. Використовуйте **fixtures** для створення тестового середовища.
4. Використовуйте **мокування** для імітації зовнішніх залежностей.
5. Тести повинні бути **незалежними** один від одного.
6. Тести повинні бути **детермінованими** (давати однакові результати при кожному запуску).
7. Тести повинні бути **швидкими** (не використовувати зовнішні ресурси без необхідності).

## Розгортання

### Фронтенд

Для збірки фронтенду:
```bash
cd frontend-app
npm run build
```

### Бекенд

Для запуску бекенду в продакшн-режимі:
```bash
cd backend-api
gunicorn app:app
```

## Додавання нової мови

Для додавання нової мови до проєкту:
1. Додайте код мови до списку підтримуваних мов у `frontend-app/next-i18next.config.js`
2. Додайте код мови до списку підтримуваних мов у `frontend-app/middleware.js`
3. Створіть директорію для нової мови у `frontend-app/public/locales`
4. Скопіюйте та перекладіть файли локалізації
5. Створіть файл локалізації для бекенду у `backend-api/locales`

Детальні інструкції можна знайти в [керівництві з інтернаціоналізації](./i18n_guide.md). 