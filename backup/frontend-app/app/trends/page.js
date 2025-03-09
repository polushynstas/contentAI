'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { API_ENDPOINTS } from '../../config/api';

export default function Trends() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasAccess, setHasAccess] = useState(false);
  const [niche, setNiche] = useState('');
  const [trends, setTrends] = useState(null);
  const [note, setNote] = useState('');

  useEffect(() => {
    // Перевіряємо, чи користувач авторизований
    const token = localStorage.getItem('token');
    
    if (!token) {
      router.push('/login');
      return;
    }

    // Перевіряємо, чи користувач має доступ до аналізу трендів
    const checkAccess = async () => {
      try {
        const response = await axios.get(API_ENDPOINTS.USER_INFO, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        const subscriptionType = response.data.subscription_type_raw;
        const isAdmin = response.data.is_admin;
        
        if (subscriptionType === 'professional' || subscriptionType === 'premium' || isAdmin) {
          setHasAccess(true);
        } else {
          setError('Для аналізу трендів потрібен професійний або преміум-план');
        }
      } catch (err) {
        console.error('Помилка при перевірці доступу:', err);
        setError('Помилка при перевірці доступу до аналізу трендів');
      }
    };

    checkAccess();
  }, [router]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!niche.trim()) {
      setError('Будь ласка, введіть нішу для аналізу');
      return;
    }

    setLoading(true);
    setError('');
    setTrends(null);
    setNote('');

    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.post(
        API_ENDPOINTS.TRENDS,
        { niche },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        setTrends({
          hashtags: response.data.hashtags || [],
          trends: response.data.trends || []
        });
        
        if (response.data.note) {
          setNote(response.data.note);
        }
      } else {
        setError(response.data.message || 'Помилка при аналізі трендів');
      }
      
      setLoading(false);
    } catch (err) {
      setLoading(false);
      console.error('Помилка при аналізі трендів:', err);
      
      if (err.response?.status === 403) {
        setError('Для аналізу трендів потрібен професійний або преміум-план');
      } else {
        setError(err.response?.data?.message || 'Помилка при аналізі трендів');
        
        // Створюємо стандартні тренди навіть у випадку помилки
        setTrends({
          hashtags: [`#${niche.toLowerCase()}`, `#${niche.toLowerCase()}trends`, `#${niche.toLowerCase()}content`, `#${niche.toLowerCase()}ideas`, `#${niche.toLowerCase()}tips`],
          trends: [
            `Короткі відео про ${niche.toLowerCase()}`,
            `Інформативні пости про ${niche.toLowerCase()}`,
            `Інтерактивний контент про ${niche.toLowerCase()}`
          ]
        });
        
        setNote('Використано стандартні тренди через помилку сервера');
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">Аналіз трендів</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {!hasAccess ? (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded mb-6">
          <p className="font-bold">Обмежений доступ</p>
          <p>Для аналізу трендів потрібен професійний або преміум-план.</p>
          <p className="mt-2">
            <a href="/subscribe" className="text-blue-600 hover:text-blue-800 underline">
              Оновити підписку
            </a>
          </p>
        </div>
      ) : (
        <>
          <div className="bg-white shadow-md rounded-lg p-6 mb-8">
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label htmlFor="niche" className="block text-gray-700 font-bold mb-2">
                  Ніша для аналізу
                </label>
                <input
                  type="text"
                  id="niche"
                  value={niche}
                  onChange={(e) => setNiche(e.target.value)}
                  placeholder="Наприклад: фітнес, кулінарія, подорожі, технології"
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              
              <div className="flex items-center justify-center">
                <button
                  type="submit"
                  disabled={loading}
                  className={`bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${
                    loading ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {loading ? 'Аналізуємо...' : 'Аналізувати тренди'}
                </button>
              </div>
            </form>
          </div>

          {trends && (
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4">Результати аналізу для ніші "{niche}"</h2>
              
              {note && (
                <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded mb-6">
                  {note}
                </div>
              )}
              
              <div className="mb-6">
                <h3 className="text-xl font-semibold mb-3">Популярні хештеги</h3>
                <div className="flex flex-wrap gap-2">
                  {trends.hashtags?.map((hashtag, index) => (
                    <span
                      key={index}
                      className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {hashtag}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold mb-3">Трендові теми</h3>
                <ul className="list-disc pl-5 space-y-2">
                  {trends.trends?.map((trend, index) => (
                    <li key={index} className="text-gray-700">
                      {trend}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
} 