import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

// Функція для перетворення camelCase в snake_case
const camelToSnakeCase = (obj) => {
  if (obj === null || obj === undefined || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(camelToSnakeCase);
  }

  return Object.keys(obj).reduce((acc, key) => {
    const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
    acc[snakeKey] = camelToSnakeCase(obj[key]);
    return acc;
  }, {});
};

// Функція для перетворення snake_case в camelCase
const snakeToCamelCase = (obj) => {
  if (obj === null || obj === undefined || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(snakeToCamelCase);
  }

  return Object.keys(obj).reduce((acc, key) => {
    const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    acc[camelKey] = snakeToCamelCase(obj[key]);
    return acc;
  }, {});
};

// Створюємо екземпляр axios
const axiosInstance = axios.create({
  baseURL: API_ENDPOINTS.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Додаємо перехоплювач запитів для перетворення camelCase в snake_case
axiosInstance.interceptors.request.use((config) => {
  if (config.data) {
    config.data = camelToSnakeCase(config.data);
  }
  if (config.params) {
    config.params = camelToSnakeCase(config.params);
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Додаємо перехоплювач відповідей для перетворення snake_case в camelCase
axiosInstance.interceptors.response.use((response) => {
  if (response.data) {
    response.data = snakeToCamelCase(response.data);
  }
  return response;
}, (error) => {
  if (error.response && error.response.data) {
    error.response.data = snakeToCamelCase(error.response.data);
  }
  return Promise.reject(error);
});

// Функція для перевірки валідності токена
export const checkTokenValidity = () => {
  const token = localStorage.getItem('token');
  if (!token) {
    return false;
  }
  
  // Тут можна додати додаткову логіку перевірки токена, наприклад, перевірку терміну дії
  
  return true;
};

// Функція для отримання інформації про користувача з localStorage
export const getUserInfo = () => {
  const userInfo = localStorage.getItem('user');
  if (!userInfo) {
    return null;
  }
  
  try {
    return JSON.parse(userInfo);
  } catch (error) {
    console.error('Помилка при парсингу інформації про користувача:', error);
    return null;
  }
};

// Функція для збереження інформації про користувача
export const saveUserInfo = (userData) => {
  try {
    localStorage.setItem('user', JSON.stringify(userData));
    return true;
  } catch (error) {
    console.error('Помилка при збереженні інформації про користувача:', error);
    return false;
  }
};

// Налаштовуємо перехоплювач для додавання токена до запитів
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default axiosInstance; 