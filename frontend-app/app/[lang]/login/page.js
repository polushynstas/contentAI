'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter, useSearchParams, useParams } from 'next/navigation';
import Link from 'next/link';
import FormInput from '../../../components/FormInput';
import { API_ENDPOINTS } from '../../../config/api';
import axiosInstance, { saveUserInfo } from '../../../utils/axios';

export default function Login() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const params = useParams();
  const lang = params.lang;
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  // Тексти для локалізації
  const translations = {
    uk: {
      title: 'Вхід',
      email: 'Email',
      emailPlaceholder: 'Введіть ваш email',
      emailRequired: 'Email обов\'язковий',
      password: 'Пароль',
      passwordPlaceholder: 'Введіть ваш пароль',
      passwordRequired: 'Пароль обов\'язковий',
      login: 'Увійти',
      loggingIn: 'Вхід...',
      noAccount: 'Немає акаунту?',
      register: 'Зареєструватися',
      registrationSuccess: 'Реєстрація успішна! Тепер ви можете увійти.',
      error: 'Помилка при вході. Перевірте ваші дані.',
      loginError: 'Помилка при вході. Перевірте ваші дані.',
      invalidCredentials: 'Неправильні облікові дані.'
    },
    en: {
      title: 'Login',
      email: 'Email',
      emailPlaceholder: 'Enter your email',
      emailRequired: 'Email is required',
      password: 'Password',
      passwordPlaceholder: 'Enter your password',
      passwordRequired: 'Password is required',
      login: 'Login',
      loggingIn: 'Logging in...',
      noAccount: 'Don\'t have an account?',
      register: 'Register',
      registrationSuccess: 'Registration successful! You can now log in.',
      error: 'Error logging in. Please check your credentials.',
      loginError: 'Error logging in. Please check your credentials.',
      invalidCredentials: 'Invalid credentials.'
    }
  };
  
  const t = translations[lang] || translations.uk;
  
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  useEffect(() => {
    // Перевіряємо, чи користувач щойно зареєструвався
    const registered = searchParams.get('registered');
    if (registered === 'true') {
      setSuccessMessage(t.registrationSuccess);
    }
  }, [searchParams, t]);
  
  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');
    
    try {
      console.log('Спроба входу...');
      
      // Використовуємо axiosInstance замість axios
      const response = await axiosInstance.post(API_ENDPOINTS.LOGIN, {
        email: data.email,
        password: data.password
      });
      
      console.log('Відповідь від сервера:', response.data);
      
      if (response.data.token) {
        // Зберігаємо токен
        localStorage.setItem('token', response.data.token);
        
        // Створюємо об'єкт з інформацією про користувача
        const userData = {
          id: response.data.user_id,
          email: response.data.email,
          isSubscribed: response.data.is_subscribed || false,
          is_admin: response.data.is_admin || false,
          name: response.data.name || '',
          subscription_type: response.data.subscription_type || 'free',
          subscription_end_date: response.data.subscription_end_date || null
        };
        
        // Зберігаємо інформацію про користувача
        saveUserInfo(userData);
        
        console.log('Збережено інформацію про користувача:', userData);
        
        // Перенаправляємо на головну сторінку або на сторінку, з якої користувач прийшов
        const redirectTo = searchParams.get('redirect') || `/${lang}`;
        router.push(redirectTo);
      } else {
        setError(t.loginError);
      }
    } catch (error) {
      console.error('Помилка при вході:', error);
      
      // Логуємо деталі помилки
      if (error.response) {
        console.error('Статус відповіді:', error.response.status);
        console.error('Дані відповіді:', error.response.data);
        
        // Встановлюємо відповідне повідомлення про помилку
        if (error.response.status === 401) {
          setError(t.invalidCredentials);
        } else {
          setError(t.loginError);
        }
      } else {
        setError(t.loginError);
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">{t.title}</h1>
      
      {successMessage && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {successMessage}
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white shadow-md rounded-lg p-6">
        <FormInput
          label={t.email}
          type="email"
          id="email"
          placeholder={t.emailPlaceholder}
          register={register('email', { 
            required: t.emailRequired
          })}
          error={errors.email}
          required
        />
        
        <FormInput
          label={t.password}
          type="password"
          id="password"
          placeholder={t.passwordPlaceholder}
          register={register('password', { 
            required: t.passwordRequired
          })}
          error={errors.password}
          required
        />
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          {isLoading ? t.loggingIn : t.login}
        </button>
      </form>
      
      <p className="text-center mt-4 text-gray-600">
        {t.noAccount}{' '}
        <Link href={`/${lang}/signup`} className="text-indigo-600 hover:text-indigo-800">
          {t.register}
        </Link>
      </p>
    </div>
  );
} 