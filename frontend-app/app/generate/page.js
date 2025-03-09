'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import FormInput from '../../components/FormInput';
import { API_ENDPOINTS } from '../../config/api';
import axiosInstance from '../../utils/axios';

export default function Generate() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSubscribed, setIsSubscribed] = useState(false);
  
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  useEffect(() => {
    // Перевіряємо, чи користувач авторизований
    const token = localStorage.getItem('token');
    
    if (!token) {
      router.push('/login');
      return;
    }
    
    // Отримуємо інформацію про користувача з localStorage
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        setIsSubscribed(userData.isSubscribed || userData.is_admin || false);
      } catch (error) {
        console.error('Помилка при отриманні інформації про користувача:', error);
      }
    }
    
    // Перевіряємо підписку на сервері
    checkSubscription();
  }, [router]);
  
  const checkSubscription = async () => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.CHECK_SUBSCRIPTION);
      
      if (response.data.isSubscribed) {
        setIsSubscribed(true);
      } else {
        setIsSubscribed(response.data.is_active);
      }
    } catch (error) {
      console.error('Помилка при перевірці підписки:', error);
    }
  };
  
  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.GENERATE, {
        niche: data.niche,
        audience: data.audience,
        platform: data.platform,
        style: data.style,
        lang: 'uk'
      });
      
      if (response.status === 200) {
        // Зберігаємо результати та перенаправляємо на сторінку результатів
        localStorage.setItem('generationResults', JSON.stringify(response.data.content));
        router.push('/results');
      }
    } catch (error) {
      console.error('Помилка при генерації ідей:', error);
      
      // Логуємо деталі помилки
      if (error.response) {
        console.error('Статус відповіді:', error.response.status);
        console.error('Дані відповіді:', error.response.data);
      }
      
      setError('Помилка при генерації ідей. Спробуйте пізніше.');
    } finally {
      setIsLoading(false);
    }
  };
  
  if (!isSubscribed) {
    return (
      <div className="max-w-md mx-auto text-center">
        <h1 className="text-3xl font-bold mb-6">Генерація ідей</h1>
        
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-6">
          <p className="font-bold">Потрібна підписка</p>
          <p>Для доступу до генерації ідей необхідна активна підписка.</p>
        </div>
        
        <button
          onClick={() => router.push('/subscribe')}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          Оформити підписку
        </button>
      </div>
    );
  }
  
  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">Генерація ідей</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white shadow-md rounded-lg p-6">
        <FormInput
          label="Ніша"
          id="niche"
          placeholder="Наприклад: фітнес, кулінарія, технології"
          register={register('niche', { required: 'Ніша обов\'язкова' })}
          error={errors.niche}
          required
        />
        
        <FormInput
          label="Аудиторія"
          id="audience"
          placeholder="Наприклад: початківці, професіонали, підлітки"
          register={register('audience', { required: 'Аудиторія обов\'язкова' })}
          error={errors.audience}
          required
        />
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Платформа <span className="text-red-500">*</span>
          </label>
          <select
            {...register('platform', { required: 'Платформа обов\'язкова' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">Виберіть платформу</option>
            <option value="YouTube">YouTube</option>
            <option value="TikTok">TikTok</option>
            <option value="Instagram">Instagram</option>
            <option value="Blog">Blog</option>
          </select>
          {errors.platform && (
            <p className="mt-1 text-sm text-red-500">{errors.platform.message}</p>
          )}
        </div>
        
        <FormInput
          label="Стиль"
          id="style"
          placeholder="Наприклад: інформативний, розважальний, навчальний"
          register={register('style', { required: 'Стиль обов\'язковий' })}
          error={errors.style}
          required
        />
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          {isLoading ? 'Генерація...' : 'Згенерувати'}
        </button>
      </form>
    </div>
  );
}
