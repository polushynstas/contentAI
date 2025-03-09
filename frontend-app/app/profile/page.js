'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';

export default function Profile() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [generations, setGenerations] = useState([]);
  const [subscriptionInfo, setSubscriptionInfo] = useState(null);
  
  useEffect(() => {
    // Перевіряємо, чи користувач авторизований
    const token = localStorage.getItem('token');
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token) {
      router.push('/login');
      return;
    }
    
    setUser(userData);
    
    // Отримуємо інформацію про користувача з бекенду
    const fetchUserInfo = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5001/user-info', {
          headers: {
            'Authorization': token
          }
        });
        
        if (response.data) {
          setSubscriptionInfo({
            isSubscribed: response.data.is_subscribed,
            subscriptionEnd: response.data.subscription_end,
            subscriptionType: response.data.subscription_type,
            subscriptionTypeRaw: response.data.subscription_type_raw
          });
          
          // Оновлюємо дані користувача в localStorage
          const updatedUserData = {
            ...userData,
            isSubscribed: response.data.is_subscribed
          };
          localStorage.setItem('user', JSON.stringify(updatedUserData));
          setUser(updatedUserData);
        }
      } catch (err) {
        console.error('Помилка при отриманні інформації про користувача:', err);
        setError('Не вдалося отримати інформацію про користувача');
      }
    };
    
    // Отримуємо історію генерацій (це буде реалізовано пізніше на бекенді)
    // Наразі використовуємо заглушку
    const mockGenerations = [
      {
        id: 1,
        date: '2023-05-15',
        niche: 'Фітнес',
        audience: 'Початківці',
        platform: 'YouTube',
        style: 'Навчальний'
      },
      {
        id: 2,
        date: '2023-05-10',
        niche: 'Кулінарія',
        audience: 'Домогосподарки',
        platform: 'TikTok',
        style: 'Розважальний'
      }
    ];
    
    setGenerations(mockGenerations);
    fetchUserInfo();
    setIsLoading(false);
  }, [router]);
  
  // Функція для форматування дати
  const formatDate = (dateString) => {
    if (!dateString) return 'Не визначено';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('uk-UA', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };
  
  // Функція для визначення статусу підписки
  const getSubscriptionStatus = () => {
    if (!subscriptionInfo || !subscriptionInfo.isSubscribed) {
      return { status: 'Неактивна', color: 'text-red-600' };
    }
    
    const now = new Date();
    const endDate = subscriptionInfo.subscriptionEnd ? new Date(subscriptionInfo.subscriptionEnd) : null;
    
    if (!endDate) {
      return { status: 'Активна', color: 'text-green-600' };
    }
    
    // Перевіряємо, чи закінчується підписка протягом 7 днів
    const daysLeft = Math.ceil((endDate - now) / (1000 * 60 * 60 * 24));
    
    if (daysLeft <= 0) {
      return { status: 'Закінчилась', color: 'text-red-600' };
    } else if (daysLeft <= 7) {
      return { status: 'Закінчується скоро', color: 'text-yellow-600' };
    } else {
      return { status: 'Активна', color: 'text-green-600' };
    }
  };
  
  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <p className="text-xl">Завантаження...</p>
      </div>
    );
  }
  
  const subscriptionStatus = getSubscriptionStatus();
  
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">Профіль користувача</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 pb-2 border-b">Інформація про користувача</h2>
        
        <div className="space-y-3">
          <div>
            <span className="font-medium">Email: </span>
            <span>{user?.email}</span>
          </div>
          
          <div>
            <span className="font-medium">Статус підписки: </span>
            <span className={subscriptionStatus.color}>
              {subscriptionStatus.status}
            </span>
          </div>
          
          {subscriptionInfo && subscriptionInfo.isSubscribed && (
            <>
              <div>
                <span className="font-medium">Тип підписки: </span>
                <span className="text-indigo-600 font-medium">
                  {subscriptionInfo.subscriptionType}
                </span>
              </div>
              
              <div>
                <span className="font-medium">Дійсна до: </span>
                <span>{formatDate(subscriptionInfo.subscriptionEnd)}</span>
              </div>
            </>
          )}
          
          <div className="mt-4">
            {!subscriptionInfo?.isSubscribed ? (
              <Link 
                href="/subscribe" 
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
              >
                Оформити підписку
              </Link>
            ) : (
              <Link 
                href="/subscribe" 
                className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
              >
                Оновити підписку
              </Link>
            )}
          </div>
        </div>
      </div>
      
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 pb-2 border-b">Історія генерацій</h2>
        
        {generations.length === 0 ? (
          <p className="text-gray-600 text-center py-4">
            У вас ще немає історії генерацій. 
            <Link href="/generate" className="text-indigo-600 hover:text-indigo-800 ml-1">
              Створіть першу ідею!
            </Link>
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ніша</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Аудиторія</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Платформа</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Стиль</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {generations.map((generation) => (
                  <tr key={generation.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{generation.date}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{generation.niche}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{generation.audience}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{generation.platform}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{generation.style}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
