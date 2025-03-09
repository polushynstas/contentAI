import { NextResponse } from 'next/server';

const defaultLocale = 'uk';
const locales = ['uk', 'en'];

// Функція для отримання локалі з запиту
function getLocale(request) {
  // Перевіряємо, чи є локаль у шляху
  const pathname = request.nextUrl.pathname;
  const pathnameLocale = locales.find(
    locale => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameLocale) return pathnameLocale;

  // Перевіряємо, чи є локаль у куках
  const cookieLocale = request.cookies.get('NEXT_LOCALE')?.value;
  if (cookieLocale && locales.includes(cookieLocale)) return cookieLocale;

  // Перевіряємо заголовок Accept-Language
  const acceptLanguage = request.headers.get('Accept-Language');
  if (acceptLanguage) {
    const acceptedLocales = acceptLanguage.split(',')
      .map(locale => locale.split(';')[0].trim())
      .find(locale => locales.some(l => locale.startsWith(l)));
    
    if (acceptedLocales) {
      const matchedLocale = locales.find(l => acceptedLocales.startsWith(l));
      if (matchedLocale) return matchedLocale;
    }
  }

  // Повертаємо локаль за замовчуванням
  return defaultLocale;
}

export function middleware(request) {
  const pathname = request.nextUrl.pathname;
  
  // Пропускаємо запити до статичних файлів та API
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // Отримуємо локаль
  const locale = getLocale(request);
  
  // Перевіряємо, чи шлях вже містить локаль
  const pathnameHasLocale = locales.some(
    locale => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameHasLocale) return NextResponse.next();

  // Перенаправляємо на шлях з локаллю
  const url = new URL(`/${locale}${pathname === '/' ? '' : pathname}`, request.url);
  url.search = request.nextUrl.search;
  
  return NextResponse.redirect(url);
}

export const config = {
  matcher: ['/((?!_next|api|.*\\.).*)'],
}; 