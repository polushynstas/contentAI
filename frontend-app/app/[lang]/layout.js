import { Inter } from 'next/font/google';
import Header from '../../components/Header';
import Footer from '../../components/Footer';
import '../globals.css';
import { getDictionary } from './dictionaries';

const inter = Inter({ subsets: ['latin'] });

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang;
  
  const dict = await getDictionary(lang);
  
  return {
    title: lang === 'uk' 
      ? 'ContentAI - Генератор ідей для контенту' 
      : 'ContentAI - Content Ideas Generator',
    description: lang === 'uk'
      ? 'Генеруйте ідеї для YouTube-відео, TikTok-постів та блогів на основі ваших параметрів'
      : 'Generate ideas for YouTube videos, TikTok posts, and blogs based on your parameters',
    keywords: lang === 'uk' ? 'контент, AI, штучний інтелект, генерація контенту' : 'content, AI, artificial intelligence, content generation',
  };
}

export default async function RootLayout({ children, params }) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang;
  
  const dict = await getDictionary(lang);
  
  return (
    <html lang={lang}>
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
