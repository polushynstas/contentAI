# ContentAI

Система для генерації контенту з використанням штучного інтелекту.

## Структура проекту

### Бекенд (backend-api)

- `app.py` - головний файл додатку Flask
- `models/` - моделі даних
  - `user/` - моделі користувачів
  - `content/` - моделі контенту
  - `payment/` - моделі платежів
- `auth/` - функціональність аутентифікації
- `content/` - функціональність генерації контенту
- `subscription/` - функціональність підписок
- `utils/` - утиліти
  - `i18n.py` - інтернаціоналізація
  - `logger.py` - логування
  - `error_handler.py` - обробка помилок
- `locales/` - файли перекладів
- `tests/` - тести

### Фронтенд (frontend-app)

- `app/` - основний код додатку Next.js
  - `[lang]/` - сторінки з підтримкою мов
  - `generate/` - сторінка генерації контенту
  - `results/` - сторінка результатів
  - `profile/` - сторінка профілю
  - `subscribe/` - сторінка підписки
- `public/` - статичні файли
- `utils/` - утиліти

## Запуск проекту

### Запуск серверів

```bash
./start_servers.sh
```

Це запустить бекенд-сервер на порту 5001 і фронтенд-сервер на порту 3000.

### Зупинка серверів

```bash
./stop_servers.sh
```

## Розробка

### Бекенд

Бекенд розроблений з використанням Flask і має модульну структуру. Кожен модуль відповідає за свою функціональність:

- `auth` - аутентифікація та авторизація
- `content` - генерація контенту
- `subscription` - управління підписками

### Фронтенд

Фронтенд розроблений з використанням Next.js і має структуру, яка відповідає маршрутам додатку.

## Технології

- Бекенд: Python, Flask, SQLAlchemy
- Фронтенд: JavaScript, React, Next.js
- API: OpenAI, Grok, Wise 