'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function SubscriptionSuccess() {
  const router = useRouter();
  
  useEffect(() => {
    // Перевіряємо, чи користувач авторизований
    const token = localStorage.getItem('token');
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token || !userData.isSubscribed) {
      router.push('/login');
    }
  }, [router]);
  
  return (
    <div className="max-w-4xl mx-auto text-center py-12">
      <div className="bg-white shadow-md rounded-lg p-8 mb-8">
        <div className="mb-6">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-12 w-12 text-green-600" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M5 13l4 4L19 7" 
              />
            </svg>
          </div>
          
          <h1 className="text-3xl font-bold mb-4">Підписку успішно оформлено!</h1>
          <p className="text-gray-600 mb-6">
            Дякуємо за підписку на ContentAI. Тепер ви маєте доступ до всіх функцій сервісу.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link 
              href="/generate" 
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg focus:outline-none focus:shadow-outline transition-colors"
            >
              Почати генерацію контенту
            </Link>
            
            <Link 
              href="/profile" 
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-6 rounded-lg focus:outline-none focus:shadow-outline transition-colors"
            >
              Перейти до профілю
            </Link>
          </div>
        </div>
      </div>
      
      <div className="bg-white shadow-md rounded-lg p-8">
        <h2 className="text-2xl font-bold mb-4">Що далі?</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-6 w-6 text-indigo-600" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" 
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Створіть ідеї</h3>
            <p className="text-gray-600">
              Використовуйте наш генератор для створення унікальних ідей для контенту.
            </p>
          </div>
          
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-6 w-6 text-indigo-600" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Перегляньте результати</h3>
            <p className="text-gray-600">
              Аналізуйте згенеровані ідеї та обирайте найкращі для вашого контенту.
            </p>
          </div>
          
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-6 w-6 text-indigo-600" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" 
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Економте час</h3>
            <p className="text-gray-600">
              Створюйте контент швидше та ефективніше з нашим сервісом.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 