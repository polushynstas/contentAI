'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';

export default function Results() {
  const router = useRouter();
  const params = useParams();
  const lang = params.lang;
  const [ideas, setIdeas] = useState([]);
  
  // Тексти для локалізації
  const translations = {
    uk: {
      title: 'Результати генерації',
      newGeneration: 'Нова генерація',
      hook: 'Хук:',
      description: 'Опис:',
      hashtags: 'Хештеги:',
      keywords: 'Ключові слова:'
    },
    en: {
      title: 'Generation Results',
      newGeneration: 'New Generation',
      hook: 'Hook:',
      description: 'Description:',
      hashtags: 'Hashtags:',
      keywords: 'Keywords:'
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
    
    // Отримуємо результати генерації з localStorage
    try {
      const resultsString = localStorage.getItem('generationResults');
      if (!resultsString) {
        router.push(`/${lang}/generate`);
        return;
      }
      
      const results = JSON.parse(resultsString);
      
      if (!results || results.length === 0) {
        // Якщо результатів немає, перенаправляємо на сторінку генерації
        router.push(`/${lang}/generate`);
        return;
      }
      
      setIdeas(results);
    } catch (error) {
      console.error('Помилка при обробці результатів:', error);
      localStorage.removeItem('generationResults'); // Видаляємо невалідні дані
      router.push(`/${lang}/generate`);
    }
  }, [router, lang]);
  
  return (
    <div className="max-w-4xl mx-auto">
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
        {ideas.map((idea, index) => (
          <div key={index} className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-bold mb-2 text-indigo-600">{idea.title}</h2>
            
            {idea.hook && (
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-1">{t.hook}</h3>
                <p className="text-gray-700">{idea.hook}</p>
              </div>
            )}
            
            <div className="mb-4">
              <h3 className="text-lg font-semibold mb-1">{t.description}</h3>
              <p className="text-gray-700">{idea.description}</p>
            </div>
            
            {idea.hashtags && idea.hashtags.length > 0 && (
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-1">{t.hashtags}</h3>
                <div className="flex flex-wrap gap-2">
                  {idea.hashtags.map((hashtag, idx) => (
                    <span key={idx} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                      {hashtag}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {idea.keywords && idea.keywords.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-1">{t.keywords}</h3>
                <div className="flex flex-wrap gap-2">
                  {idea.keywords.map((keyword, idx) => (
                    <span key={idx} className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
} 