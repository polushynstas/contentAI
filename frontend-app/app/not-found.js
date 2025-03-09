import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
      <h1 className="text-6xl font-bold mb-4 text-indigo-600">404</h1>
      <h2 className="text-3xl font-semibold mb-6">Сторінку не знайдено</h2>
      
      <p className="text-xl mb-8 max-w-md text-gray-600">
        Вибачте, сторінка, яку ви шукаєте, не існує або була переміщена.
      </p>
      
      <Link 
        href="/" 
        className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-lg transition-colors"
      >
        Повернутися на головну
      </Link>
    </div>
  );
}
