'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import LanguageSwitcher from './LanguageSwitcher';

const Header = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentLocale, setCurrentLocale] = useState('uk');
  const pathname = usePathname();
  
  // Тексти для мов
  const translations = {
    uk: {
      home: 'Головна',
      login: 'Увійти',
      signup: 'Реєстрація',
      logout: 'Вийти',
      generate: 'Генерація ідей',
      trends: 'Тренди',
      subscription: 'Підписки',
      profile: 'Профіль'
    },
    en: {
      home: 'Home',
      login: 'Login',
      signup: 'Sign Up',
      logout: 'Logout',
      generate: 'Generate Ideas',
      trends: 'Trends',
      subscription: 'Subscription',
      profile: 'Profile'
    }
  };
  
  useEffect(() => {
    // Визначаємо поточну локаль з URL
    const pathParts = pathname.split('/');
    if (pathParts.length > 1 && (pathParts[1] === 'uk' || pathParts[1] === 'en')) {
      setCurrentLocale(pathParts[1]);
    }
  }, [pathname]);
  
  const checkAuth = () => {
    // Перевіряємо, чи є токен у localStorage
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      setIsLoggedIn(!!token);
      console.log('Перевірка авторизації:', !!token);
    }
  };
  
  useEffect(() => {
    // Перевіряємо авторизацію при монтуванні компонента
    checkAuth();
    
    // Додаємо обробник події storage для відстеження змін у localStorage
    const handleStorageChange = () => {
      checkAuth();
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Додаємо власну подію для відстеження змін авторизації
    window.addEventListener('authChange', handleStorageChange);
    
    // Додаємо інтервал для періодичної перевірки авторизації
    const interval = setInterval(() => {
      checkAuth();
    }, 1000); // Перевіряємо кожну секунду
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('authChange', handleStorageChange);
      clearInterval(interval);
    };
  }, []);
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    
    // Створюємо подію для оновлення стану авторизації
    const event = new Event('authChange');
    window.dispatchEvent(event);
    
    window.location.href = `/${currentLocale}`;
  };
  
  // Функція для отримання шляху з поточною локаллю
  const getLocalizedPath = (path) => {
    return `/${currentLocale}${path}`;
  };
  
  return (
    <header className="bg-indigo-700 text-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="text-xl font-bold">
            <Link href={getLocalizedPath('/')} className="hover:text-indigo-200">
              ContentAI
            </Link>
          </div>
          
          <nav className="flex items-center">
            <ul className="flex space-x-6 mr-6">
              <li>
                <Link href={getLocalizedPath('/')} className="hover:text-indigo-200">
                  {translations[currentLocale].home}
                </Link>
              </li>
              {isLoggedIn ? (
                <>
                  <li>
                    <Link href={getLocalizedPath('/generate')} className="hover:text-indigo-200">
                      {translations[currentLocale].generate}
                    </Link>
                  </li>
                  <li>
                    <Link href={getLocalizedPath('/trends')} className="hover:text-indigo-200">
                      {translations[currentLocale].trends}
                    </Link>
                  </li>
                  <li>
                    <Link href={getLocalizedPath('/subscribe')} className="hover:text-indigo-200">
                      {translations[currentLocale].subscription}
                    </Link>
                  </li>
                  <li>
                    <Link href={getLocalizedPath('/profile')} className="hover:text-indigo-200">
                      {translations[currentLocale].profile}
                    </Link>
                  </li>
                  <li>
                    <button 
                      onClick={handleLogout} 
                      className="hover:text-indigo-200"
                    >
                      {translations[currentLocale].logout}
                    </button>
                  </li>
                </>
              ) : (
                <>
                  <li>
                    <Link href={getLocalizedPath('/login')} className="hover:text-indigo-200">
                      {translations[currentLocale].login}
                    </Link>
                  </li>
                  <li>
                    <Link href={getLocalizedPath('/signup')} className="hover:text-indigo-200">
                      {translations[currentLocale].signup}
                    </Link>
                  </li>
                </>
              )}
            </ul>
            <LanguageSwitcher />
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
