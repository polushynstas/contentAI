'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axios from 'axios';
import { API_ENDPOINTS } from '../../../config/api';

export default function Trends() {
  const router = useRouter();
  const params = useParams();
  const lang = params.lang;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasAccess, setHasAccess] = useState(false);
  const [niche, setNiche] = useState('');
  const [trends, setTrends] = useState(null);
  const [note, setNote] = useState('');

  // Тексти для локалізації
  const translations = {
    uk: {
      title: 'Аналіз трендів',
      nicheLabel: 'Ніша для аналізу',
      nichePlaceholder: 'Наприклад: фітнес, кулінарія, подорожі, технології',
      analyzeButton: 'Аналізувати тренди',
      analyzing: 'Аналізуємо...',
      resultsTitle: 'Результати аналізу для ніші',
      hashtagsTitle: 'Популярні хештеги',
      trendsTitle: 'Трендові теми',
      limitedAccess: 'Обмежений доступ',
      needPlan: 'Для аналізу трендів потрібен професійний або преміум-план.',
      upgradeSubscription: 'Оновити підписку',
      emptyNicheError: 'Будь ласка, введіть нішу для аналізу',
      accessError: 'Для аналізу трендів потрібен професійний або преміум-план',
      generalError: 'Помилка при аналізі трендів',
      defaultNote: 'Використано стандартні тренди через помилку сервера'
    },
    en: {
      title: 'Trend Analysis',
      nicheLabel: 'Niche for analysis',
      nichePlaceholder: 'For example: fitness, cooking, travel, technology',
      analyzeButton: 'Analyze Trends',
      analyzing: 'Analyzing...',
      resultsTitle: 'Analysis results for niche',
      hashtagsTitle: 'Popular Hashtags',
      trendsTitle: 'Trending Topics',
      limitedAccess: 'Limited Access',
      needPlan: 'Professional or premium plan is required for trend analysis.',
      upgradeSubscription: 'Upgrade Subscription',
      emptyNicheError: 'Please enter a niche for analysis',
      accessError: 'Professional or premium plan is required for trend analysis',
      generalError: 'Error analyzing trends',
      defaultNote: 'Default trends used due to server error'
    }
  };
  
  const t = translations[lang] || translations.uk;

  useEffect(() => {
    // Перевіряємо, чи користувач авторизований
    const token = localStorage.getItem('token');
    
    if (!token) {
      router.push(`/${lang}/login`);
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
          setError(t.accessError);
        }
      } catch (err) {
        console.error('Помилка при перевірці доступу:', err);
        setError(t.accessError);
      }
    };

    checkAccess();
  }, [router, lang, t]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!niche.trim()) {
      setError(t.emptyNicheError);
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
        setError(response.data.message || t.generalError);
      }
      
      setLoading(false);
    } catch (err) {
      setLoading(false);
      console.error('Помилка при аналізі трендів:', err);
      
      if (err.response?.status === 403) {
        setError(t.accessError);
      } else {
        setError(err.response?.data?.message || t.generalError);
        
        // Створюємо стандартні тренди навіть у випадку помилки
        setTrends({
          hashtags: [`#${niche.toLowerCase()}`, `#${niche.toLowerCase()}trends`, `#${niche.toLowerCase()}content`, `#${niche.toLowerCase()}ideas`, `#${niche.toLowerCase()}tips`],
          trends: [
            `Короткі відео про ${niche.toLowerCase()}`,
            `Інформативні пости про ${niche.toLowerCase()}`,
            `Інтерактивний контент про ${niche.toLowerCase()}`
          ]
        });
        
        setNote(t.defaultNote);
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">{t.title}</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {!hasAccess ? (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded mb-6">
          <p className="font-bold">{t.limitedAccess}</p>
          <p>{t.needPlan}</p>
          <p className="mt-2">
            <a href={`/${lang}/subscribe`} className="text-blue-600 hover:text-blue-800 underline">
              {t.upgradeSubscription}
            </a>
          </p>
        </div>
      ) : (
        <>
          <div className="bg-white shadow-md rounded-lg p-6 mb-8">
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label htmlFor="niche" className="block text-gray-700 font-bold mb-2">
                  {t.nicheLabel}
                </label>
                <input
                  type="text"
                  id="niche"
                  value={niche}
                  onChange={(e) => setNiche(e.target.value)}
                  placeholder={t.nichePlaceholder}
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
                  {loading ? t.analyzing : t.analyzeButton}
                </button>
              </div>
            </form>
          </div>

          {trends && (
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4">{t.resultsTitle} "{niche}"</h2>
              
              {note && (
                <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded mb-6">
                  {note}
                </div>
              )}
              
              <div className="mb-6">
                <h3 className="text-xl font-semibold mb-3">{t.hashtagsTitle}</h3>
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
                <h3 className="text-xl font-semibold mb-3">{t.trendsTitle}</h3>
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