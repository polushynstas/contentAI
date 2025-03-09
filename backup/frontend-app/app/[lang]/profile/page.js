'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axios from 'axios';
import { API_ENDPOINTS } from '../../../config/api';

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
    const token = localStorage.getItem('token');
    
    if (!token) {
      setIsLoading(false);
      return;
    }
    
    const fetchUserProfile = async () => {
      try {
        const response = await axios.get(API_ENDPOINTS.PROFILE, {
          headers: { Authorization: `Bearer ${token}` },
          params: { lang: lang }
        });
        
        if (response.status === 200) {
          setUser(response.data);
        }
      } catch (err) {
        setError(t.error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUserProfile();
  }, [t]);
  
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