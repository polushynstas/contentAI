'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { API_ENDPOINTS } from '../../../config/api';
import axiosInstance, { checkTokenValidity, getUserInfo } from '../../../utils/axios';

export default function Profile() {
  const router = useRouter();
  const params = useParams();
  const lang = params.lang;
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Тексти для локалізації
  const translations = {
    uk: {
      title: 'Профіль',
      email: 'Email',
      subscriptionStatus: 'Статус підписки',
      active: 'Активна',
      inactive: 'Неактивна',
      subscribe: 'Оформити підписку',
      loading: 'Завантаження...',
      error: 'Помилка при завантаженні профілю. Спробуйте пізніше.',
      notLoggedIn: 'Ви не авторизовані. Будь ласка, увійдіть в систему.',
      login: 'Увійти'
    },
    en: {
      title: 'Profile',
      email: 'Email',
      subscriptionStatus: 'Subscription Status',
      active: 'Active',
      inactive: 'Inactive',
      subscribe: 'Subscribe',
      loading: 'Loading...',
      error: 'Error loading profile. Please try again later.',
      notLoggedIn: 'You are not logged in. Please log in.',
      login: 'Login'
    }
  };
  
  const t = translations[lang] || translations.uk;
  
  useEffect(() => {
    // Перевіряємо валідність токена при завантаженні сторінки
    if (!checkTokenValidity()) {
      console.log('Токен недійсний або відсутній, перенаправлення на сторінку входу');
      router.push(`/${lang}/login`);
      return;
    }
    
    // Спочатку використовуємо збережену інформацію про користувача
    const savedUser = getUserInfo();
    if (savedUser) {
      console.log('Використовуємо збережену інформацію про користувача:', savedUser);
      setUser(savedUser);
      setIsLoading(false);
    }
    
    // Потім оновлюємо інформацію з сервера
    fetchUserInfo();
  }, [lang, router]);

  const fetchUserInfo = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      console.log('Отримання інформації про користувача з сервера...');
      
      // Використовуємо axiosInstance замість axios
      const response = await axiosInstance.get(API_ENDPOINTS.USER_INFO);
      
      console.log('Відповідь від сервера:', response.data);
      setUser(response.data);
    } catch (error) {
      console.error('Помилка при отриманні інформації про користувача:', error);
      
      // Логуємо деталі помилки
      if (error.response) {
        console.error('Статус відповіді:', error.response.status);
        console.error('Дані відповіді:', error.response.data);
      }
      
      // Якщо у нас вже є збережена інформація про користувача, не показуємо помилку
      if (!user) {
        setError(translations[lang].error);
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="max-w-md mx-auto text-center py-12">
        <p className="text-lg">{t.loading}</p>
      </div>
    );
  }
  
  if (!localStorage.getItem('token')) {
    return (
      <div className="max-w-md mx-auto text-center">
        <h1 className="text-3xl font-bold mb-6">{t.title}</h1>
        
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-6">
          <p>{t.notLoggedIn}</p>
        </div>
        
        <button
          onClick={() => router.push(`/${lang}/login`)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          {t.login}
        </button>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="max-w-md mx-auto text-center">
        <h1 className="text-3xl font-bold mb-6">{t.title}</h1>
        
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">{t.title}</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6">
        <div className="mb-4">
          <h2 className="text-sm font-medium text-gray-500">{t.email}</h2>
          <p className="text-lg">{user?.email}</p>
        </div>
        
        <div className="mb-6">
          <h2 className="text-sm font-medium text-gray-500">{t.subscriptionStatus}</h2>
          <p className="text-lg">
            {user?.is_subscribed ? (
              <span className="text-green-600">{t.active}</span>
            ) : (
              <span className="text-red-600">{t.inactive}</span>
            )}
          </p>
        </div>
        
        {!user?.is_subscribed && (
          <button
            onClick={() => router.push(`/${lang}/subscribe`)}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
          >
            {t.subscribe}
          </button>
        )}
      </div>
    </div>
  );
} 