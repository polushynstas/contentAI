'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import FormInput from '../../components/FormInput';
import { API_ENDPOINTS } from '../../config/api';

export default function Signup() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
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
            router.push('/');
          }
        } catch (loginErr) {
          // Якщо автоматична авторизація не вдалася, перенаправляємо на сторінку логіну
          router.push('/login?registered=true');
        }
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Помилка при реєстрації. Спробуйте пізніше.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">Реєстрація</h1>
      
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
            required: 'Email обов\'язковий',
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: 'Невірний формат email'
            }
          })}
          error={errors.email}
          required
        />
        
        <FormInput
          label="Пароль"
          type="password"
          id="password"
          placeholder="Створіть пароль"
          register={register('password', { 
            required: 'Пароль обов\'язковий',
            minLength: {
              value: 6,
              message: 'Пароль має містити щонайменше 6 символів'
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
          {isLoading ? 'Реєстрація...' : 'Зареєструватися'}
        </button>
      </form>
      
      <p className="text-center mt-4 text-gray-600">
        Вже маєте акаунт?{' '}
        <Link href="/login" className="text-indigo-600 hover:text-indigo-800">
          Увійти
        </Link>
      </p>
    </div>
  );
}
