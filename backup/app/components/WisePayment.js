'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

export default function WisePayment({ planId, planPrice, onSuccess, onError }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paymentDetails, setPaymentDetails] = useState({
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    cardholderName: ''
  });
  const [paymentStatus, setPaymentStatus] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPaymentDetails({
      ...paymentDetails,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Отримуємо токен з локального сховища
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('Ви не авторизовані');
      }

      // Відправляємо запит на оновлення підписки
      const response = await axios.post(
        'http://127.0.0.1:5001/update-subscription',
        { plan: planId },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      // Перевіряємо успішність запиту
      if (response.data.success) {
        // Якщо є інформація про платіж, зберігаємо її
        if (response.data.payment) {
          setPaymentStatus({
            id: response.data.payment.id,
            status: response.data.payment.status,
            amount: response.data.payment.amount,
            currency: response.data.payment.currency
          });

          // Перевіряємо статус платежу через 2 секунди
          setTimeout(() => checkPaymentStatus(response.data.payment.id), 2000);
        } else {
          // Якщо немає інформації про платіж (безкоштовний план), повідомляємо про успіх
          if (onSuccess) {
            onSuccess(response.data);
          }
        }
      } else {
        throw new Error(response.data.message || 'Помилка при оновленні підписки');
      }
    } catch (err) {
      console.error('Помилка при оплаті:', err);
      setError(err.message || 'Помилка при обробці платежу');
      if (onError) {
        onError(err);
      }
    } finally {
      setLoading(false);
    }
  };

  // Функція для перевірки статусу платежу
  const checkPaymentStatus = async (paymentId) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('Ви не авторизовані');
      }

      const response = await axios.get(
        `http://127.0.0.1:5001/check-payment/${paymentId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        const payment = response.data.payment;
        setPaymentStatus({
          id: payment.id,
          status: payment.status,
          amount: payment.amount,
          currency: payment.currency
        });

        // Якщо платіж завершено, повідомляємо про успіх
        if (payment.status === 'completed') {
          if (onSuccess) {
            onSuccess(response.data);
          }
        } else if (payment.status === 'pending') {
          // Якщо платіж все ще в обробці, перевіряємо знову через 2 секунди
          setTimeout(() => checkPaymentStatus(paymentId), 2000);
        } else if (payment.status === 'failed') {
          // Якщо платіж не вдався, повідомляємо про помилку
          throw new Error('Платіж не вдався');
        }
      } else {
        throw new Error(response.data.message || 'Помилка при перевірці статусу платежу');
      }
    } catch (err) {
      console.error('Помилка при перевірці статусу платежу:', err);
      setError(err.message || 'Помилка при перевірці статусу платежу');
      if (onError) {
        onError(err);
      }
    }
  };

  return (
    <div className="payment-form">
      <h3 className="text-xl font-semibold mb-4">Оплата через Wise</h3>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {paymentStatus ? (
        <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded mb-4">
          <p><strong>Статус платежу:</strong> {paymentStatus.status === 'pending' ? 'В обробці' : paymentStatus.status === 'completed' ? 'Завершено' : 'Помилка'}</p>
          <p><strong>Сума:</strong> {paymentStatus.amount} {paymentStatus.currency}</p>
          <p><strong>ID платежу:</strong> {paymentStatus.id}</p>
          {paymentStatus.status === 'pending' && (
            <p className="mt-2">Очікуйте, платіж обробляється...</p>
          )}
          {paymentStatus.status === 'completed' && (
            <p className="mt-2">Платіж успішно оброблено! Ваша підписка активована.</p>
          )}
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="cardNumber">
              Номер картки
            </label>
            <input
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="cardNumber"
              name="cardNumber"
              type="text"
              placeholder="1234 5678 9012 3456"
              value={paymentDetails.cardNumber}
              onChange={handleInputChange}
              required
            />
          </div>
          
          <div className="flex mb-4">
            <div className="w-1/2 mr-2">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="expiryDate">
                Термін дії
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="expiryDate"
                name="expiryDate"
                type="text"
                placeholder="MM/YY"
                value={paymentDetails.expiryDate}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="w-1/2 ml-2">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="cvv">
                CVV
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="cvv"
                name="cvv"
                type="text"
                placeholder="123"
                value={paymentDetails.cvv}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="cardholderName">
              Ім'я власника картки
            </label>
            <input
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="cardholderName"
              name="cardholderName"
              type="text"
              placeholder="Іван Петренко"
              value={paymentDetails.cardholderName}
              onChange={handleInputChange}
              required
            />
          </div>
          
          <div className="flex items-center justify-between">
            <button
              className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
              type="submit"
              disabled={loading}
            >
              {loading ? 'Обробка...' : `Оплатити ${planPrice} USD`}
            </button>
          </div>
        </form>
      )}
    </div>
  );
} 