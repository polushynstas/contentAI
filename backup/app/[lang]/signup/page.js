'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import FormInput from '../../../components/FormInput';
import { API_ENDPOINTS } from '../../../config/api';

export default function Signup() {
  const router = useRouter();
  const params = useParams();
  const lang = params.lang;
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Тексти для локалізації
  const translations = {
    uk: {
      title: 'Реєстрація',
      email: 'Email',
      emailPlaceholder: 'Введіть ваш email',
      emailRequired: 'Email обов\'язковий',
      emailInvalid: 'Невірний формат email',
      password: 'Пароль',
      passwordPlaceholder: 'Створіть пароль',
      passwordRequired: 'Пароль обов\'язковий',
      passwordTooShort: 'Пароль має містити щонайменше 6 символів',
      register: 'Зареєструватися',
      registering: 'Реєстрація...',
      haveAccount: 'Вже маєте акаунт?',
      login: 'Увійти',
      error: 'Помилка при реєстрації. Спробуйте пізніше.'
    },
    en: {
      title: 'Sign Up',
      email: 'Email',
      emailPlaceholder: 'Enter your email',
      emailRequired: 'Email is required',
      emailInvalid: 'Invalid email format',
      password: 'Password',
      passwordPlaceholder: 'Create a password',
      passwordRequired: 'Password is required',
      passwordTooShort: 'Password must be at least 6 characters',
      register: 'Register',
      registering: 'Registering...',
      haveAccount: 'Already have an account?',
      login: 'Login',
      error: 'Error during registration. Please try again later.'
    }
  };
  
  const t = translations[lang] || translations.uk;
  
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');
    
    try {
      // Реєстрація користувача
      const signupResponse = await axios.post(API_ENDPOINTS.SIGNUP, {
        email: data.email,
        password: data.password
      });
      
      if (signupResponse.status === 201) {
        // Після успішної реєстрації автоматично авторизуємо користувача
        try {
          const loginResponse = await axios.post(API_ENDPOINTS.LOGIN, {
            email: data.email,
            password: data.password
          });
          
          if (loginResponse.status === 200) {
            // Зберігаємо токен та інформацію про користувача
            localStorage.setItem('token', loginResponse.data.token);
            localStorage.setItem('user', JSON.stringify({
              id: loginResponse.data.user_id,
              email: loginResponse.data.email,
              isSubscribed: loginResponse.data.is_subscribed
            }));
            
            // Створюємо подію для оновлення стану авторизації
            const event = new Event('authChange');
            window.dispatchEvent(event);
            
            // Перенаправляємо на головну сторінку
            router.push(`/${lang}`);
          }
        } catch (loginErr) {
          // Якщо автоматична авторизація не вдалася, перенаправляємо на сторінку логіну
          router.push(`/${lang}/login?registered=true`);
        }
      }
    } catch (err) {
      setError(err.response?.data?.message || t.error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">{t.title}</h1>
      
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
            required: t.emailRequired,
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: t.emailInvalid
            }
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
            required: t.passwordRequired,
            minLength: {
              value: 6,
              message: t.passwordTooShort
            }
          })}
          error={errors.password}
          required
        />
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          {isLoading ? t.registering : t.register}
        </button>
      </form>
      
      <p className="text-center mt-4 text-gray-600">
        {t.haveAccount}{' '}
        <Link href={`/${lang}/login`} className="text-indigo-600 hover:text-indigo-800">
          {t.login}
        </Link>
      </p>
    </div>
  );
} 