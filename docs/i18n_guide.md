# Керівництво з інтернаціоналізації ContentAI

Цей документ містить інструкції щодо роботи з інтернаціоналізацією (i18n) у проєкті ContentAI.

## Загальна інформація

Проєкт ContentAI підтримує багатомовність за допомогою:
- На фронтенді: Next.js App Router з параметром `[lang]`
- На бекенді: Flask з параметром `lang` у запитах

Наразі підтримуються такі мови:
- Українська (`uk`) - мова за замовчуванням
- Англійська (`en`)

## Фронтенд

### Структура локалізаційних файлів

Локалізаційні файли знаходяться у директорії `frontend-app/public/locales` і організовані за наступною структурою:

```
public/
  locales/
    uk/
      auth/
        common.json
      subscription/
        common.json
      profile/
        common.json
      ...
    en/
      auth/
        common.json
      subscription/
        common.json
      profile/
        common.json
      ...
```

### Використання локалізації у компонентах

#### Серверні компоненти

Для серверних компонентів використовуйте функцію `getDictionary`:

```jsx
// app/[lang]/page.js
import { getDictionary } from './dictionaries'

export default async function Page({ params: { lang } }) {
  const dictionary = await getDictionary(lang, 'auth')
  
  return (
    <div>
      <h1>{dictionary.login}</h1>
      <p>{dictionary.login_description}</p>
    </div>
  )
}
```

#### Клієнтські компоненти

Для клієнтських компонентів використовуйте хук `useTranslation`:

```jsx
// app/components/LoginForm.js
'use client'

import { useTranslation } from '@/app/i18n/client'

export default function LoginForm({ lang }) {
  const { t } = useTranslation(lang, 'auth')
  
  return (
    <form>
      <label>{t('email')}</label>
      <input type="email" placeholder={t('email_placeholder')} />
      <label>{t('password')}</label>
      <input type="password" placeholder={t('password_placeholder')} />
      <button type="submit">{t('login_button')}</button>
    </form>
  )
}
```

### Маршрутизація з урахуванням мови

Для створення посилань з урахуванням мови використовуйте компонент `Link` з Next.js:

```jsx
import Link from 'next/link'

export default function LanguageSwitcher({ lang }) {
  return (
    <div>
      <Link href={`/uk${pathname}`} locale="uk">
        Українська
      </Link>
      <Link href={`/en${pathname}`} locale="en">
        English
      </Link>
    </div>
  )
}
```

### Конфігурація

Конфігурація інтернаціоналізації знаходиться у файлі `frontend-app/next-i18next.config.js`:

```js
module.exports = {
  i18n: {
    defaultLocale: 'uk',
    locales: ['uk', 'en'],
  },
}
```

Також налаштування маршрутизації знаходяться у файлі `frontend-app/middleware.js`:

```js
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}

export function middleware(request) {
  const pathname = request.nextUrl.pathname
  
  // Перевірка, чи URL вже має префікс локалі
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  )
  
  if (pathnameHasLocale) return
  
  // Визначення локалі з заголовка Accept-Language
  const locale = request.headers.get('Accept-Language')?.split(',')[0].split('-')[0] || 'uk'
  
  // Перенаправлення на URL з префіксом локалі
  return NextResponse.redirect(new URL(`/${locale}${pathname}`, request.url))
}
```

## Бекенд

### Структура локалізаційних файлів

Локалізаційні файли знаходяться у директорії `backend-api/locales` і організовані за наступною структурою:

```
locales/
  uk.json
  en.json
```

Кожен файл містить JSON-об'єкт з перекладами, організованими за модулями:

```json
{
  "auth": {
    "login_success": "Вхід успішний",
    "login_failed": "Невірний email або пароль",
    "signup_success": "Користувач успішно зареєстрований",
    "signup_failed": "Помилка реєстрації"
  },
  "subscription": {
    "subscription_active": "Ваша підписка активна",
    "subscription_expired": "Ваша підписка закінчилася",
    "subscription_updated": "Підписка успішно оновлена"
  },
  "content": {
    "generation_success": "Контент успішно згенеровано",
    "generation_failed": "Помилка генерації контенту"
  }
}
```

### Використання локалізації в маршрутах

Для використання локалізації в маршрутах використовуйте функцію `load_translations`:

```python
from utils.i18n import load_translations

@app.route('/api/endpoint', methods=['GET'])
def endpoint():
    # Отримання мови з параметра запиту
    lang = request.args.get('lang', 'uk')
    
    # Завантаження перекладів
    translations = load_translations(lang)
    
    # Використання перекладів
    return jsonify({
        'message': translations['auth']['login_success']
    })
```

Для маршрутів, захищених декоратором `token_required`, переклади передаються як параметр:

```python
@app.route('/api/protected', methods=['GET'])
@token_required
def protected_route(current_user, lang='uk', translations=None):
    return jsonify({
        'message': translations['auth']['login_success']
    })
```

### Функція завантаження перекладів

Функція `load_translations` знаходиться у файлі `backend-api/utils/i18n.py`:

```python
import os
import json

def load_translations(lang='uk'):
    """
    Завантажує переклади для вказаної мови.
    
    Args:
        lang (str): Код мови (uk або en)
        
    Returns:
        dict: Словник з перекладами
    """
    # Шлях до файлу з перекладами
    locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
    locale_file = os.path.join(locales_dir, f'{lang}.json')
    
    # Якщо файл не існує, використовуємо українську мову за замовчуванням
    if not os.path.exists(locale_file):
        locale_file = os.path.join(locales_dir, 'uk.json')
    
    # Завантаження перекладів
    try:
        with open(locale_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Помилка завантаження перекладів: {str(e)}")
        return {}
```

## Додавання нової мови

### Фронтенд

1. Додайте код нової мови до списку підтримуваних мов у `frontend-app/next-i18next.config.js`:

```js
module.exports = {
  i18n: {
    defaultLocale: 'uk',
    locales: ['uk', 'en', 'pl'],  // Додано польську мову
  },
}
```

2. Додайте код нової мови до списку підтримуваних мов у `frontend-app/middleware.js`:

```js
const locales = ['uk', 'en', 'pl']  // Додано польську мову
```

3. Створіть директорію для нової мови у `frontend-app/public/locales`:

```
mkdir -p frontend-app/public/locales/pl/auth
mkdir -p frontend-app/public/locales/pl/subscription
mkdir -p frontend-app/public/locales/pl/profile
```

4. Скопіюйте файли локалізації з існуючої мови та перекладіть їх:

```
cp frontend-app/public/locales/en/auth/common.json frontend-app/public/locales/pl/auth/common.json
cp frontend-app/public/locales/en/subscription/common.json frontend-app/public/locales/pl/subscription/common.json
cp frontend-app/public/locales/en/profile/common.json frontend-app/public/locales/pl/profile/common.json
```

### Бекенд

1. Створіть файл локалізації для нової мови у `backend-api/locales`:

```
cp backend-api/locales/en.json backend-api/locales/pl.json
```

2. Перекладіть вміст файлу на нову мову.

## Тестування локалізації

### Фронтенд

Для тестування локалізації на фронтенді:

1. Запустіть сервер розробки:

```
cd frontend-app
npm run dev
```

2. Відкрийте браузер і перейдіть за адресою:
   - Українська: http://localhost:3000/uk
   - Англійська: http://localhost:3000/en
   - Нова мова: http://localhost:3000/pl

### Бекенд

Для тестування локалізації на бекенді:

1. Запустіть сервер розробки:

```
cd backend-api
python app.py
```

2. Відправте запит з параметром `lang`:

```
curl -X GET "http://localhost:5001/health?lang=en"
curl -X GET "http://localhost:5001/health?lang=pl"
```

## Найкращі практики

1. **Використовуйте ключі, а не значення**:
   ```jsx
   // Правильно
   <button>{t('login_button')}</button>
   
   // Неправильно
   <button>{t('Увійти')}</button>
   ```

2. **Організуйте переклади за модулями**:
   ```
   auth/common.json
   subscription/common.json
   profile/common.json
   ```

3. **Використовуйте параметри в перекладах**:
   ```json
   {
     "welcome": "Вітаємо, {{name}}!"
   }
   ```
   
   ```jsx
   <p>{t('welcome', { name: user.name })}</p>
   ```

4. **Перевіряйте наявність усіх ключів у всіх мовах**:
   Переконайтеся, що всі ключі, які є в одній мові, присутні і в інших мовах.

5. **Використовуйте значення за замовчуванням**:
   ```jsx
   const dictionary = await getDictionary(lang, 'auth')
   const loginText = dictionary.login || 'Увійти'
   ```

6. **Тестуйте всі мови**:
   Переконайтеся, що ваш додаток працює коректно з усіма підтримуваними мовами. 