'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

export default function Checkout({ plan, onClose }) {
  const router = useRouter();
  const [formData, setFormData] = useState({
    cardNumber: '',
    cardName: '',
    expiryDate: '',
    cvv: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [paymentError, setPaymentError] = useState('');

  // Функція для обробки змін у формі
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Очищаємо помилку для поля, яке змінюється
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  // Функція для валідації форми
  const validateForm = () => {
    const newErrors = {};
    
    // Валідація номера картки (16 цифр)
    if (!formData.cardNumber.trim() || !/^\d{16}$/.test(formData.cardNumber.replace(/\s/g, ''))) {
      newErrors.cardNumber = 'Введіть правильний номер картки (16 цифр)';
    }
    
    // Валідація імені власника картки
    if (!formData.cardName.trim()) {
      newErrors.cardName = 'Введіть ім\'я власника картки';
    }
    
    // Валідація терміну дії (формат MM/YY)
    if (!formData.expiryDate.trim() || !/^\d{2}\/\d{2}$/.test(formData.expiryDate)) {
      newErrors.expiryDate = 'Введіть термін дії у форматі MM/YY';
    } else {
      // Перевірка, чи не закінчився термін дії
      const [month, year] = formData.expiryDate.split('/');
      const expiryDate = new Date(2000 + parseInt(year), parseInt(month) - 1);
      const currentDate = new Date();
      
      if (expiryDate < currentDate) {
        newErrors.expiryDate = 'Термін дії картки закінчився';
      }
    }
    
    // Валідація CVV (3 цифри)
    if (!formData.cvv.trim() || !/^\d{3}$/.test(formData.cvv)) {
      newErrors.cvv = 'Введіть правильний CVV код (3 цифри)';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Функція для обробки відправки форми
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Валідація форми
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setPaymentError('');
    
    try {
      // Отримуємо токен з localStorage
      const token = localStorage.getItem('token');
      
      if (!token) {
        router.push('/login');
        return;
      }
      
      // Відправляємо запит на оновлення підписки
      const response = await axios.post(
        'http://127.0.0.1:5001/update-subscription',
        { plan: plan.id },
        {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data && response.data.is_subscribed) {
        // Оновлюємо дані користувача в localStorage
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        const updatedUserData = {
          ...userData,
          isSubscribed: true
        };
        localStorage.setItem('user', JSON.stringify(updatedUserData));
        
        // Перенаправляємо на сторінку успішної підписки
        router.push('/subscribe/success');
      } else {
        setPaymentError('Не вдалося оновити підписку. Спробуйте ще раз.');
      }
    } catch (error) {
      console.error('Помилка при оновленні підписки:', error);
      setPaymentError(
        error.response?.data?.message || 
        'Виникла помилка при обробці платежу. Спробуйте ще раз.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Оформлення підписки</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2">{plan.name}</h3>
          <p className="text-gray-600 mb-2">{plan.description}</p>
          <p className="text-2xl font-bold text-indigo-600">{plan.price} $ / місяць</p>
        </div>
        
        {paymentError && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {paymentError}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="cardNumber">
              Номер картки
            </label>
            <input
              type="text"
              id="cardNumber"
              name="cardNumber"
              value={formData.cardNumber}
              onChange={handleChange}
              placeholder="1234 5678 9012 3456"
              className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                errors.cardNumber ? 'border-red-500' : ''
              }`}
            />
            {errors.cardNumber && (
              <p className="text-red-500 text-xs italic">{errors.cardNumber}</p>
            )}
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="cardName">
              Ім'я власника картки
            </label>
            <input
              type="text"
              id="cardName"
              name="cardName"
              value={formData.cardName}
              onChange={handleChange}
              placeholder="IVAN IVANOV"
              className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                errors.cardName ? 'border-red-500' : ''
              }`}
            />
            {errors.cardName && (
              <p className="text-red-500 text-xs italic">{errors.cardName}</p>
            )}
          </div>
          
          <div className="flex mb-4">
            <div className="w-1/2 mr-2">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="expiryDate">
                Термін дії
              </label>
              <input
                type="text"
                id="expiryDate"
                name="expiryDate"
                value={formData.expiryDate}
                onChange={handleChange}
                placeholder="MM/YY"
                className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                  errors.expiryDate ? 'border-red-500' : ''
                }`}
              />
              {errors.expiryDate && (
                <p className="text-red-500 text-xs italic">{errors.expiryDate}</p>
              )}
            </div>
            
            <div className="w-1/2 ml-2">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="cvv">
                CVV
              </label>
              <input
                type="text"
                id="cvv"
                name="cvv"
                value={formData.cvv}
                onChange={handleChange}
                placeholder="123"
                className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                  errors.cvv ? 'border-red-500' : ''
                }`}
              />
              {errors.cvv && (
                <p className="text-red-500 text-xs italic">{errors.cvv}</p>
              )}
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <button
              type="submit"
              disabled={isLoading}
              className={`bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? 'Обробка...' : 'Оплатити'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 