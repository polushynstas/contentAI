'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import WisePayment from '../../../app/components/WisePayment';
import axios from 'axios';
import { API_ENDPOINTS } from '../../../config/api';

export default function Subscribe() {
  const router = useRouter();
  const params = useParams();
  const lang = params.lang;
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showPayment, setShowPayment] = useState(false);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [subscription, setSubscription] = useState(null);
  
  // Тексти для локалізації
  const translations = {
    uk: {
      title: 'Підписки',
      choosePlan: 'Оберіть план підписки',
      accessDescription: 'Отримайте доступ до генерації ідей для контенту з використанням Grok AI',
      loading: 'Завантаження...',
      currentSubscription: 'Ваша поточна підписка',
      plan: 'План',
      validUntil: 'Діє до',
      backToPlans: '← Повернутися до планів',
      youSelected: 'Ви обрали план',
      for: 'за',
      monthly: 'місяць',
      recommended: 'Рекомендовано',
      allPlansInfo: 'Усі плани (крім пробного) — щомісячні з автоподовженням, яке можна скасувати.',
      trialInfo: 'Пробний період одноразовий, автоматично завершується через 7 днів або переходить у базовий план, якщо не вибрати інший.',
      backToHome: 'Повернутися на головну',
      subscriptionError: 'Не вдалося отримати інформацію про підписку',
      paymentSuccess: 'Підписку успішно оновлено до плану',
      paymentError: 'Помилка при обробці платежу',
      unknownError: 'Невідома помилка',
      days: 'днів',
      trial: {
        name: 'Пробний план',
        description: 'Ідеально для тестування сервісу перед покупкою повноцінної підписки',
        features: [
          '5 запитів',
          'Генерація 3 ідей за запит',
          'Підтримка TikTok, YouTube, Instagram, блогів',
          'Стилі: інформативний, розважальний, навчальний',
          'Актуальні тренди з X у реальному часі',
          'Доступ до базової документації'
        ],
        buttonText: 'Спробувати за $1'
      },
      basic: {
        name: 'Базовий план',
        description: 'Для початківців, які хочуть регулярно генерувати ідеї',
        features: [
          '15 запитів на місяць',
          'Усе з пробного плану',
          'Підтримка через email (відповідь до 48 годин)'
        ],
        buttonText: 'Обрати базовий план'
      },
      professional: {
        name: 'Професійний план',
        description: 'Для професіоналів, які потребують більше запитів і аналітики',
        features: [
          '30 запитів на місяць',
          'Усе з базового плану',
          'Додаткові стилі: історія, мотиваційний, розважально-освітній',
          'Аналітика трендів: популярні хештеги і трендові теми',
          'Експорт ідей у PDF або CSV',
          'Пріоритетна підтримка (відповідь до 24 годин)'
        ],
        buttonText: 'Обрати професійний план'
      },
      premium: {
        name: 'Преміум-план',
        description: 'Для агенцій, великих блогерів і компаній з кількома креаторами',
        features: [
          '50 запитів на місяць',
          'Усе з професійного плану',
          'Мультикористувацький доступ: до 3 акаунтів',
          'Інтеграція з планувальниками: Later, Buffer',
          'Персоналізовані трендові звіти',
          'Просунута підтримка (телефон/Zoom, відповідь до 12 годин)'
        ],
        buttonText: 'Обрати преміум-план'
      }
    },
    en: {
      title: 'Subscriptions',
      choosePlan: 'Choose a Subscription Plan',
      accessDescription: 'Get access to content idea generation using Grok AI',
      loading: 'Loading...',
      currentSubscription: 'Your Current Subscription',
      plan: 'Plan',
      validUntil: 'Valid until',
      backToPlans: '← Back to Plans',
      youSelected: 'You selected',
      for: 'for',
      monthly: 'month',
      recommended: 'Recommended',
      allPlansInfo: 'All plans (except trial) are monthly with auto-renewal, which can be canceled.',
      trialInfo: 'The trial period is one-time, automatically ends after 7 days or transitions to the basic plan if you don\'t choose another.',
      backToHome: 'Back to Home',
      subscriptionError: 'Failed to get subscription information',
      paymentSuccess: 'Subscription successfully updated to',
      paymentError: 'Error processing payment',
      unknownError: 'Unknown error',
      days: 'days',
      trial: {
        name: 'Trial Plan',
        description: 'Perfect for testing the service before purchasing a full subscription',
        features: [
          '5 requests',
          'Generation of 3 ideas per request',
          'Support for TikTok, YouTube, Instagram, blogs',
          'Styles: informative, entertaining, educational',
          'Real-time trends from X',
          'Access to basic documentation'
        ],
        buttonText: 'Try for $1'
      },
      basic: {
        name: 'Basic Plan',
        description: 'For beginners who want to regularly generate ideas',
        features: [
          '15 requests per month',
          'Everything from the trial plan',
          'Email support (response within 48 hours)'
        ],
        buttonText: 'Choose Basic Plan'
      },
      professional: {
        name: 'Professional Plan',
        description: 'For professionals who need more requests and analytics',
        features: [
          '30 requests per month',
          'Everything from the basic plan',
          'Additional styles: story, motivational, edutainment',
          'Trend analytics: popular hashtags and trending topics',
          'Export ideas to PDF or CSV',
          'Priority support (response within 24 hours)'
        ],
        buttonText: 'Choose Professional Plan'
      },
      premium: {
        name: 'Premium Plan',
        description: 'For agencies, large bloggers, and companies with multiple creators',
        features: [
          '50 requests per month',
          'Everything from the professional plan',
          'Multi-user access: up to 3 accounts',
          'Integration with schedulers: Later, Buffer',
          'Personalized trend reports',
          'Advanced support (phone/Zoom, response within 12 hours)'
        ],
        buttonText: 'Choose Premium Plan'
      }
    }
  };
  
  const t = translations[lang] || translations.uk;
  
  useEffect(() => {
    // Перевіряємо, чи користувач авторизований
    const token = localStorage.getItem('token');
    
    if (!token) {
      router.push(`/${lang}/login`);
    }
  }, [router, lang]);
  
  useEffect(() => {
    fetchSubscriptionStatus();
  }, []);

  const fetchSubscriptionStatus = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push(`/${lang}/login`);
        return;
      }

      const response = await axios.get(API_ENDPOINTS.CHECK_SUBSCRIPTION, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        params: {
          lang: lang
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
        text: t.subscriptionError
      });
    } finally {
      setLoading(false);
    }
  };
  
  const plans = [
    {
      id: 'trial',
      name: t.trial.name,
      price: '1',
      period: `7 ${t.days}`,
      description: t.trial.description,
      features: t.trial.features,
      recommended: false,
      buttonText: t.trial.buttonText
    },
    {
      id: 'basic',
      name: t.basic.name,
      price: '15',
      period: t.monthly,
      description: t.basic.description,
      features: t.basic.features,
      recommended: false,
      buttonText: t.basic.buttonText
    },
    {
      id: 'professional',
      name: t.professional.name,
      price: '30',
      period: t.monthly,
      description: t.professional.description,
      features: t.professional.features,
      recommended: true,
      buttonText: t.professional.buttonText
    },
    {
      id: 'premium',
      name: t.premium.name,
      price: '50',
      period: t.monthly,
      description: t.premium.description,
      features: t.premium.features,
      recommended: false,
      buttonText: t.premium.buttonText
    }
  ];
  
  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    setShowPayment(true);
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
      text: `${t.paymentSuccess} ${selectedPlan.name}!`
    });
  };
  
  const handlePaymentError = (error) => {
    console.error('Помилка при обробці платежу:', error);
    setMessage({
      type: 'error',
      text: `${t.paymentError}: ${error.message || t.unknownError}`
    });
  };
  
  if (showPayment && selectedPlan) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8">{t.choosePlan}</h1>
        
        <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
          <button 
            onClick={() => setShowPayment(false)}
            className="mb-4 text-indigo-600 hover:text-indigo-800"
          >
            {t.backToPlans}
          </button>
          
          <h2 className="text-2xl font-bold mb-4">{selectedPlan.name}</h2>
          <p className="text-gray-600 mb-6">{t.youSelected} {selectedPlan.name} {t.for} ${selectedPlan.price} / {selectedPlan.period}</p>
          
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
      <h1 className="text-3xl font-bold mb-6">{t.title}</h1>
      
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
          <p className="text-gray-600">{t.loading}</p>
        </div>
      ) : (
        <div>
          {subscription && (
            <div className="mb-8 p-4 bg-blue-50 rounded-lg">
              <h2 className="text-xl font-semibold mb-2">{t.currentSubscription}</h2>
              <p><strong>{t.plan}:</strong> {subscription.plan.charAt(0).toUpperCase() + subscription.plan.slice(1)}</p>
              {subscription.expiry && (
                <p><strong>{t.validUntil}:</strong> {subscription.expiry.toLocaleDateString(lang === 'uk' ? 'uk-UA' : 'en-US')}</p>
              )}
            </div>
          )}
          
          <div className="max-w-6xl mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-2 text-center">{t.choosePlan}</h1>
            <p className="text-gray-600 text-center mb-12">{t.accessDescription}</p>
            
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
                      {t.recommended}
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
              <p className="text-gray-600 mb-4">{t.allPlansInfo}</p>
              <p className="text-gray-600 mb-8">{t.trialInfo}</p>
              
              <Link 
                href={`/${lang}`} 
                className="text-indigo-600 hover:text-indigo-800 font-medium"
              >
                {t.backToHome}
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 