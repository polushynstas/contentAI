module.exports = {
  i18n: {
    defaultLocale: 'uk',
    locales: ['uk', 'en'],
    localeDetection: true,
  },
  localePath: './public/locales',
  reloadOnPrerender: process.env.NODE_ENV === 'development',
} 