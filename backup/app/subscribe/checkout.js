'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Checkout({ plan, onCancel }) {
  const router = useRouter();
  const [formData, setFormData] = useState({
    cardNumber: '',
    cardName: '',
    expiryDate: '',
    cvv: '',
    agreeTerms: false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Валідація форми
    if (!formData.cardNumber || !formData.cardName || !formData.expiryDate || !formData.cvv) {
      setError('Будь ласка, заповніть усі поля');
      return;
    }
    
    if (!formData.agreeTerms) {
      setError('Будь ласка, погодьтеся з умовами використання');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      // Тут буде логіка для обробки платежу
      // Наразі просто імітуємо успішну оплату
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Оновлюємо статус підписки користувача в localStorage
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      user.isSubscribed = true;
      user.subscriptionPlan = plan.id;
      localStorage.setItem('user', JSON.stringify(user));
      
      // Перенаправляємо на сторінку успішної оплати
      router.push('/subscribe/success');
    } catch (err) {
      setError('Помилка при обробці платежу. Спробуйте пізніше.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-center">Оформлення підписки</h2>
      
      <div className="bg-gray-50 p-4 rounded-lg mb-6">
        <h3 className="font-medium text-gray-900">{plan.name}</h3>
        <div className="flex items-baseline mt-1">
          <span className="text-2xl font-bold text-gray-900">{plan.price}</span>
          <span className="text-gray-500 ml-1">/{plan.period}</span>
        </div>
        <p className="text-sm text-gray-600 mt-2">{plan.description}</p>
      </div>
      
      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded-lg mb-6">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Номер картки
          </label>
          <input
            type="text"
            name="cardNumber"
            value={formData.cardNumber}
            onChange={handleChange}
            placeholder="1234 5678 9012 3456"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            required
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Ім'я на картці
          </label>
          <input
            type="text"
            name="cardName"
            value={formData.cardName}
            onChange={handleChange}
            placeholder="Іван Петренко"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            required
          />
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Термін дії
            </label>
            <input
              type="text"
              name="expiryDate"
              value={formData.expiryDate}
              onChange={handleChange}
              placeholder="MM/РР"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              CVV
            </label>
            <input
              type="text"
              name="cvv"
              value={formData.cvv}
              onChange={handleChange}
              placeholder="123"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
          </div>
        </div>
        
        <div className="mb-6">
          <div className="flex items-start">
            <input
              type="checkbox"
              name="agreeTerms"
              checked={formData.agreeTerms}
              onChange={handleChange}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded mt-1"
              required
            />
            <label className="ml-2 block text-sm text-gray-700">
              Я погоджуюся з <a href="#" className="text-indigo-600 hover:text-indigo-800">умовами використання</a> та <a href="#" className="text-indigo-600 hover:text-indigo-800">політикою конфіденційності</a>
            </label>
          </div>
        </div>
        
        <div className="flex space-x-4">
          <button
            type="button"
            onClick={onCancel}
            className="w-1/2 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Назад
          </button>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-1/2 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {isLoading ? 'Обробка...' : 'Оплатити'}
          </button>
        </div>
      </form>
    </div>
  );
} 