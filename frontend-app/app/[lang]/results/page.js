'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';

export default function Results() {
  const router = useRouter();
  const params = useParams();
  const lang = params.lang;
  const [results, setResults] = useState(null);
  
  // Тексти для локалізації
  const translations = {
    uk: {
      title: 'Результати генерації',
      newGeneration: 'Нова генерація',
      hashtags: 'Хештеги:',
      trends: 'Тренди:',
      noResults: 'Немає результатів. Спробуйте згенерувати нові ідеї.',
      copyToClipboard: 'Копіювати',
      copied: 'Скопійовано!'
    },
    en: {
      title: 'Generation Results',
      newGeneration: 'New Generation',
      hashtags: 'Hashtags:',
      trends: 'Trends:',
      noResults: 'No results. Try generating new ideas.',
      copyToClipboard: 'Copy',
      copied: 'Copied!'
    }
  };
  
  const t = translations[lang] || translations.uk;
  const [copyStatus, setCopyStatus] = useState({});
  
  useEffect(() => {
    // Перевіряємо, чи користувач авторизований
    const token = localStorage.getItem('token');
    
    if (!token) {
      router.push(`/${lang}/login`);
      return;
    }
    
    // Отримуємо результати генерації з localStorage
    try {
      const resultsString = localStorage.getItem('generationResults');
      if (!resultsString) {
        router.push(`/${lang}/generate`);
        return;
      }
      
      const parsedResults = JSON.parse(resultsString);
      
      if (!parsedResults || (!parsedResults.hashtags && !parsedResults.trends)) {
        // Якщо результатів немає або вони не містять потрібних полів, перенаправляємо на сторінку генерації
        router.push(`/${lang}/generate`);
        return;
      }
      
      setResults(parsedResults);
    } catch (error) {
      console.error('Помилка при отриманні результатів:', error);
      router.push(`/${lang}/generate`);
    }
  }, [router, lang]);
  
  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopyStatus({ ...copyStatus, [id]: true });
      setTimeout(() => {
        setCopyStatus({ ...copyStatus, [id]: false });
      }, 2000);
    });
  };
  
  if (!results) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6 text-center">{t.title}</h1>
        <p className="text-center">{t.noResults}</p>
        <div className="mt-6 flex justify-center">
          <Link 
            href={`/${lang}/generate`} 
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition-colors"
          >
            {t.newGeneration}
          </Link>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">{t.title}</h1>
      
      <div className="mb-6 flex justify-center">
        <Link 
          href={`/${lang}/generate`} 
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          {t.newGeneration}
        </Link>
      </div>
      
      <div className="space-y-6">
        {/* Хештеги */}
        {results.hashtags && results.hashtags.length > 0 && (
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-indigo-600">{t.hashtags}</h2>
            <div className="flex flex-wrap gap-2">
              {results.hashtags.map((hashtag, index) => (
                <div key={index} className="bg-gray-100 rounded-full px-4 py-2 flex items-center">
                  <span className="mr-2">{hashtag}</span>
                  <button 
                    onClick={() => copyToClipboard(hashtag, `hashtag-${index}`)}
                    className="text-gray-500 hover:text-indigo-600"
                    title={t.copyToClipboard}
                  >
                    {copyStatus[`hashtag-${index}`] ? (
                      <span className="text-green-500 text-xs">{t.copied}</span>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Тренди */}
        {results.trends && results.trends.length > 0 && (
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-indigo-600">{t.trends}</h2>
            <ul className="space-y-3">
              {results.trends.map((trend, index) => (
                <li key={index} className="flex justify-between items-center bg-gray-50 p-3 rounded">
                  <span>{trend}</span>
                  <button 
                    onClick={() => copyToClipboard(trend, `trend-${index}`)}
                    className="text-gray-500 hover:text-indigo-600 ml-2"
                    title={t.copyToClipboard}
                  >
                    {copyStatus[`trend-${index}`] ? (
                      <span className="text-green-500 text-xs">{t.copied}</span>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
} 