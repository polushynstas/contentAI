'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import FormInput from '../../components/FormInput';
import { API_ENDPOINTS } from '../../config/api';

export default function Login() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  useEffect(() => {
    // Перевіряємо, чи користувач щойно зареєструвався
    const registered = searchParams.get('registered');
    if (registered === 'true') {
      setSuccessMessage('Реєстрація успішна! Тепер ви можете увійти.');
    }
  }, [searchParams]);
  
  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');
    
    console.log('Спроба входу з даними:', { email: data.email });
    console.log('Використовуємо URL:', API_ENDPOINTS.LOGIN);
    
    try {
      console.log('Відправляємо запит на вхід...');
      const response = await axios.post(API_ENDPOINTS.LOGIN, {
        email: data.email,
        password: data.password
      });
      
      console.log('Отримано відповідь:', response.status, response.data);
      
      if (response.status === 200) {
        console.log('Вхід успішний, зберігаємо токен...');
        // Зберігаємо токен та інформацію про користувача
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify({
          id: response.data.user_id,
          email: response.data.email,
          isSubscribed: response.data.is_subscribed
        }));
        
        console.log('Створюємо подію authChange...');
        // Створюємо подію для оновлення стану авторизації
        const event = new Event('authChange');
        window.dispatchEvent(event);
        
        console.log('Перенаправляємо на головну сторінку...');
        // Перенаправляємо на головну сторінку
        router.push('/');
      }
    } catch (err) {
      console.error('Помилка при вході:', err);
      console.error('Деталі помилки:', err.response?.data);
      setError(err.response?.data?.message || 'Помилка при вході. Перевірте ваші дані.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">Вхід</h1>
      
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
          label="Email"
          type="email"
          id="email"
          placeholder="Введіть ваш email"
          register={register('email', { 
            required: 'Email обов\'язковий'
          })}
          error={errors.email}
          required
        />
        
        <FormInput
          label="Пароль"
          type="password"
          id="password"
          placeholder="Введіть ваш пароль"
          register={register('password', { 
            required: 'Пароль обов\'язковий'
          })}
          error={errors.password}
          required
        />
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          {isLoading ? 'Вхід...' : 'Увійти'}
        </button>
      </form>
      
      <p className="text-center mt-4 text-gray-600">
        Немає акаунту?{' '}
        <Link href="/signup" className="text-indigo-600 hover:text-indigo-800">
          Зареєструватися
        </Link>
      </p>
    </div>
  );
}
