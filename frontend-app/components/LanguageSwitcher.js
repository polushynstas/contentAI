'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';

const LanguageSwitcher = () => {
  const router = useRouter();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [currentLocale, setCurrentLocale] = useState('uk');

  useEffect(() => {
    // Визначаємо поточну локаль з URL
    const pathParts = pathname.split('/');
    if (pathParts.length > 1 && (pathParts[1] === 'uk' || pathParts[1] === 'en')) {
      setCurrentLocale(pathParts[1]);
    }
  }, [pathname]);

  // Функція для отримання шляху з новою локаллю
  const getPathWithNewLocale = (newLocale) => {
    const pathParts = pathname.split('/');
    if (pathParts.length > 1 && (pathParts[1] === 'uk' || pathParts[1] === 'en')) {
      pathParts[1] = newLocale;
    }
    return pathParts.join('/');
  };

  // Тексти для мов
  const languageTexts = {
    uk: {
      uk: 'Українська',
      en: 'Англійська'
    },
    en: {
      uk: 'Ukrainian',
      en: 'English'
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-1 text-white hover:text-indigo-200 focus:outline-none"
      >
        <span>{languageTexts[currentLocale][currentLocale]}</span>
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d={isOpen ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"}
          ></path>
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10">
          <Link
            href={getPathWithNewLocale('uk')}
            className={`block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-100 w-full text-left ${
              currentLocale === 'uk' ? 'bg-indigo-50' : ''
            }`}
            onClick={() => {
              setIsOpen(false);
              document.cookie = `NEXT_LOCALE=uk; path=/; max-age=31536000`;
            }}
          >
            {languageTexts[currentLocale]['uk']}
          </Link>
          <Link
            href={getPathWithNewLocale('en')}
            className={`block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-100 w-full text-left ${
              currentLocale === 'en' ? 'bg-indigo-50' : ''
            }`}
            onClick={() => {
              setIsOpen(false);
              document.cookie = `NEXT_LOCALE=en; path=/; max-age=31536000`;
            }}
          >
            {languageTexts[currentLocale]['en']}
          </Link>
        </div>
      )}
    </div>
  );
};

export default LanguageSwitcher; 