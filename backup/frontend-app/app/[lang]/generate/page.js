'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import { useRouter, useParams } from 'next/navigation';
import FormInput from '../../../components/FormInput';
import { API_ENDPOINTS } from '../../../config/api';

export default function Generate() {
  const router = useRouter();
  const params = useParams();
  const lang = params.lang;
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSubscribed, setIsSubscribed] = useState(false);
  
  // Тексти для локалізації
  const translations = {
    uk: {
      title: 'Генерація ідей',
      subscriptionRequired: 'Потрібна підписка',
      subscriptionText: 'Для доступу до генерації ідей необхідна активна підписка.',
      subscribe: 'Оформити підписку',
      niche: 'Ніша',
      nichePlaceholder: 'Наприклад: фітнес, кулінарія, технології',
      nicheRequired: 'Ніша обов\'язкова',
      audience: 'Аудиторія',
      audiencePlaceholder: 'Наприклад: початківці, професіонали, підлітки',
      audienceRequired: 'Аудиторія обов\'язкова',
      platform: 'Платформа',
      platformRequired: 'Платформа обов\'язкова',
      choosePlatform: 'Виберіть платформу',
      style: 'Стиль',
      stylePlaceholder: 'Наприклад: інформативний, розважальний, навчальний',
      styleRequired: 'Стиль обов\'язковий',
      generate: 'Згенерувати',
      generating: 'Генерація...',
      error: 'Помилка при генерації ідей. Спробуйте пізніше.',
      subscriptionError: 'Для генерації ідей потрібна активна підписка. Будь ласка, оформіть підписку.'
    },
    en: {
      title: 'Generate Ideas',
      subscriptionRequired: 'Subscription Required',
      subscriptionText: 'An active subscription is required to access idea generation.',
      subscribe: 'Subscribe',
      niche: 'Niche',
      nichePlaceholder: 'For example: fitness, cooking, technology',
      nicheRequired: 'Niche is required',
      audience: 'Audience',
      audiencePlaceholder: 'For example: beginners, professionals, teenagers',
      audienceRequired: 'Audience is required',
      platform: 'Platform',
      platformRequired: 'Platform is required',
      choosePlatform: 'Choose a platform',
      style: 'Style',
      stylePlaceholder: 'For example: informative, entertaining, educational',
      styleRequired: 'Style is required',
      generate: 'Generate',
      generating: 'Generating...',
      error: 'Error generating ideas. Please try again later.',
      subscriptionError: 'An active subscription is required to generate ideas. Please subscribe.'
    }
  };
  
  const t = translations[lang] || translations.uk;
  
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  useEffect(() => {
    // Перевіряємо, чи користувач авторизований
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token) {
      router.push(`/${lang}/login`);
      return;
    }
    
    // Перевіряємо статус підписки або адміністратора
    setIsSubscribed(user.isSubscribed || user.is_admin || false);
    
    // Додатково можна перевірити статус підписки через API
    const checkSubscription = async () => {
      try {
        const response = await axios.get(API_ENDPOINTS.CHECK_SUBSCRIPTION, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // Якщо користувач адміністратор, завжди дозволяємо доступ
        if (response.data.is_admin) {
          setIsSubscribed(true);
        } else {
          setIsSubscribed(response.data.is_active);
        }
      } catch (err) {
        console.error('Помилка при перевірці підписки:', err);
      }
    };
    
    checkSubscription();
  }, [router, lang]);
  
  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');
    
    const token = localStorage.getItem('token');
    
    if (!token) {
      router.push(`/${lang}/login`);
      return;
    }
    
    try {
      const response = await axios.post(API_ENDPOINTS.GENERATE, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.status === 200) {
        // Зберігаємо результати та перенаправляємо на сторінку результатів
        localStorage.setItem('generationResults', JSON.stringify(response.data.content));
        router.push(`/${lang}/results`);
      }
    } catch (err) {
      if (err.response?.status === 403) {
        setError(t.subscriptionError);
      } else {
        setError(err.response?.data?.message || t.error);
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  if (!isSubscribed) {
    return (
      <div className="max-w-md mx-auto text-center">
        <h1 className="text-3xl font-bold mb-6">{t.title}</h1>
        
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-6">
          <p className="font-bold">{t.subscriptionRequired}</p>
          <p>{t.subscriptionText}</p>
        </div>
        
        <button
          onClick={() => router.push(`/${lang}/subscribe`)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          {t.subscribe}
        </button>
      </div>
    );
  }
  
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
          label={t.niche}
          id="niche"
          placeholder={t.nichePlaceholder}
          register={register('niche', { required: t.nicheRequired })}
          error={errors.niche}
          required
        />
        
        <FormInput
          label={t.audience}
          id="audience"
          placeholder={t.audiencePlaceholder}
          register={register('audience', { required: t.audienceRequired })}
          error={errors.audience}
          required
        />
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t.platform} <span className="text-red-500">*</span>
          </label>
          <select
            {...register('platform', { required: t.platformRequired })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">{t.choosePlatform}</option>
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
          label={t.style}
          id="style"
          placeholder={t.stylePlaceholder}
          register={register('style', { required: t.styleRequired })}
          error={errors.style}
          required
        />
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          {isLoading ? t.generating : t.generate}
        </button>
      </form>
    </div>
  );
} 