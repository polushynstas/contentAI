import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'ContentAI - генератор ідей для контенту',
  description: 'Генеруйте ідеї для контенту за допомогою штучного інтелекту',
};

export default function RootLayout({ children }) {
  return (
    <html lang="uk">
      <head>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet" />
      </head>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}