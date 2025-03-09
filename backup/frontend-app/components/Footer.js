'use client';

import React, { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';

const Footer = () => {
  const [currentLocale, setCurrentLocale] = useState('uk');
  const pathname = usePathname();
  
  // Тексти для мов
  const translations = {
    uk: {
      slogan: 'Генеруй ідеї для контенту швидко та легко',
      copyright: '© 2025 ContentAI. Всі права захищено.'
    },
    en: {
      slogan: 'Generate content ideas quickly and easily',
      copyright: '© 2025 ContentAI. All rights reserved.'
    }
  };
  
  useEffect(() => {
    // Визначаємо поточну локаль з URL
    const pathParts = pathname.split('/');
    if (pathParts.length > 1 && (pathParts[1] === 'uk' || pathParts[1] === 'en')) {
      setCurrentLocale(pathParts[1]);
    }
  }, [pathname]);

  return (
    <footer className="bg-gray-800 text-white py-6 mt-auto">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-lg font-bold">ContentAI</p>
            <p className="text-sm text-gray-400">{translations[currentLocale].slogan}</p>
          </div>
          
          <div className="text-sm text-gray-400">
            <p>{translations[currentLocale].copyright.replace('2025', new Date().getFullYear())}</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
