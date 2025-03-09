'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Checkout from '../components/Checkout';
import WisePayment from '../../app/components/WisePayment';
import axios from 'axios';

export default function Subscribe() {
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showCheckout, setShowCheckout] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [subscription, setSubscription] = useState(null);
  
  useEffect(() => {
    // Перевіряємо, чи користувач авторизований
    const token = localStorage.getItem('token');
    
    if (!token) {
      router.push('/login');
    }
  }, [router]);
  
  useEffect(() => {
    fetchSubscriptionStatus();
  }, []);

  const fetchSubscriptionStatus = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await axios.get('http://127.0.0.1:5001/check-subscription', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.data.success) {
        setSubscription({
          plan: response.data.subscription,
          expiry: response.data.expiry ? new Date(response.data.expiry) : null
        });
      }
    } catch (error) {
      console.error('Помилка при отриманні статусу підписки:', error);
      setMessage({
        type: 'error',
        text: 'Не вдалося отримати інформацію про підписку'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const plans = [
    {
      id: 'trial',
      name: 'Пробний план',
      price: '1',
      period: '7 днів',
      description: 'Ідеально для тестування сервісу перед покупкою повноцінної підписки',
      features: [
        '5 запитів',
        'Генерація 3 ідей за запит',
        'Підтримка TikTok, YouTube, Instagram, блогів',
        'Стилі: інформативний, розважальний, навчальний',
        'Актуальні тренди з X у реальному часі',
        'Доступ до базової документації'
      ],
      recommended: false,
      buttonText: 'Спробувати за $1'
    },
    {
      id: 'basic',
      name: 'Базовий план',
      price: '15',
      period: 'місяць',
      description: 'Для початківців, які хочуть регулярно генерувати ідеї',
      features: [
        '15 запитів на місяць',
        'Усе з пробного плану',
        'Підтримка через email (відповідь до 48 годин)'
      ],
      recommended: false,
      buttonText: 'Обрати базовий план'
    },
    {
      id: 'professional',
      name: 'Професійний план',
      price: '30',
      period: 'місяць',
      description: 'Для професіоналів, які потребують більше запитів і аналітики',
      features: [
        '30 запитів на місяць',
        'Усе з базового плану',
        'Додаткові стилі: історія, мотиваційний, розважально-освітній',
        'Аналітика трендів: популярні хештеги і трендові теми',
        'Експорт ідей у PDF або CSV',
        'Пріоритетна підтримка (відповідь до 24 годин)'
      ],
      recommended: true,
      buttonText: 'Обрати професійний план'
    },
    {
      id: 'premium',
      name: 'Преміум-план',
      price: '50',
      period: 'місяць',
      description: 'Для агенцій, великих блогерів і компаній з кількома креаторами',
      features: [
        '50 запитів на місяць',
        'Усе з професійного плану',
        'Мультикористувацький доступ: до 3 акаунтів',
        'Інтеграція з планувальниками: Later, Buffer',
        'Персоналізовані трендові звіти',
        'Просунута підтримка (телефон/Zoom, відповідь до 12 годин)'
      ],
      recommended: false,
      buttonText: 'Обрати преміум-план'
    }
  ];
  
  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    setShowPayment(true);
  };
  
  const handleCancelCheckout = () => {
    setShowCheckout(false);
    setSelectedPlan(null);
  };
  
  const handlePaymentSuccess = (data) => {
    console.log('Платіж успішно оброблено:', data);
    setShowPayment(false);
    setSelectedPlan(null);
    
    // Оновлюємо інформацію про підписку користувача
    fetchSubscriptionStatus();
    
    // Показуємо повідомлення про успішну оплату
    setMessage({
      type: 'success',
      text: `Підписку успішно оновлено до плану ${selectedPlan.name}!`
    });
  };
  
  const handlePaymentError = (error) => {
    console.error('Помилка при обробці платежу:', error);
    setMessage({
      type: 'error',
      text: `Помилка при обробці платежу: ${error.message || 'Невідома помилка'}`
    });
  };
  
  if (showPayment && selectedPlan) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8">Оберіть план підписки</h1>
        
        <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
          <button 
            onClick={() => setShowPayment(false)}
            className="mb-4 text-indigo-600 hover:text-indigo-800"
          >
            ← Повернутися до планів
          </button>
          
          <h2 className="text-2xl font-bold mb-4">{selectedPlan.name}</h2>
          <p className="text-gray-600 mb-6">Ви обрали план {selectedPlan.name} за ${selectedPlan.price} / {selectedPlan.period}</p>
          
          <WisePayment 
            planId={selectedPlan.id}
            planPrice={selectedPlan.price}
            onSuccess={handlePaymentSuccess}
            onError={handlePaymentError}
          />
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Підписки</h1>
      
      {message && (
        <div className={`mb-4 p-4 rounded ${message.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {message.text}
          <button 
            className="ml-2 text-sm"
            onClick={() => setMessage(null)}
          >
            ✕
          </button>
        </div>
      )}
      
      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-600">Завантаження...</p>
        </div>
      ) : (
        <div>
          {subscription && (
            <div className="mb-8 p-4 bg-blue-50 rounded-lg">
              <h2 className="text-xl font-semibold mb-2">Ваша поточна підписка</h2>
              <p><strong>План:</strong> {subscription.plan.charAt(0).toUpperCase() + subscription.plan.slice(1)}</p>
              {subscription.expiry && (
                <p><strong>Діє до:</strong> {subscription.expiry.toLocaleDateString('uk-UA')}</p>
              )}
            </div>
          )}
          
          <div className="max-w-6xl mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-2 text-center">Оберіть план підписки</h1>
            <p className="text-gray-600 text-center mb-12">Отримайте доступ до генерації ідей для контенту з використанням Grok AI</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {plans.map((plan) => (
                <div 
                  key={plan.id} 
                  className={`bg-white rounded-xl shadow-lg overflow-hidden transition-transform hover:scale-105 ${
                    plan.recommended ? 'border-2 border-indigo-500 relative' : ''
                  }`}
                >
                  {plan.recommended && (
                    <div className="bg-indigo-500 text-white text-xs font-bold py-1 px-3 absolute top-0 right-0 rounded-bl-lg">
                      Рекомендовано
                    </div>
                  )}
                  
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                    <div className="flex items-baseline mb-4">
                      <span className="text-3xl font-extrabold text-gray-900">{plan.price}</span>
                      <span className="text-gray-500 ml-1"> $ / {plan.period}</span>
                    </div>
                    <p className="text-gray-600 mb-6">{plan.description}</p>
                    
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, index) => (
                        <li key={index} className="flex items-start">
                          <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                          </svg>
                          <span className="text-gray-700">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="px-6 pb-6">
                    <button
                      onClick={() => handleSelectPlan(plan)}
                      className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                        plan.recommended
                          ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                      }`}
                    >
                      {plan.buttonText}
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-12 text-center">
              <p className="text-gray-600 mb-4">Усі плани (крім пробного) — щомісячні з автоподовженням, яке можна скасувати.</p>
              <p className="text-gray-600 mb-8">Пробний період одноразовий, автоматично завершується через 7 днів або переходить у базовий план, якщо не вибрати інший.</p>
              
              <Link 
                href="/" 
                className="text-indigo-600 hover:text-indigo-800 font-medium"
              >
                Повернутися на головну
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
