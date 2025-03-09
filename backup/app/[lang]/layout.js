import { Inter } from 'next/font/google';
import Header from '../../components/Header';
import Footer from '../../components/Footer';
import '../globals.css';
import { getDictionary } from './dictionaries';

const inter = Inter({ subsets: ['latin'] });

export async function generateMetadata({ params }) {
  const dict = await getDictionary(params.lang);
  
  return {
    title: params.lang === 'uk' 
      ? 'ContentAI - Генератор ідей для контенту' 
      : 'ContentAI - Content Ideas Generator',
    description: params.lang === 'uk'
      ? 'Генеруйте ідеї для YouTube-відео, TikTok-постів та блогів на основі ваших параметрів'
      : 'Generate ideas for YouTube videos, TikTok posts, and blogs based on your parameters',
  };
}

export default async function RootLayout({ children, params }) {
  return (
    <html lang={params.lang}>
      <head>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet" />
      </head>
      <body className={`${inter.className} min-h-screen flex flex-col bg-gray-50`}>
        <Header />
        <main className="flex-grow container mx-auto px-4 py-8">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
