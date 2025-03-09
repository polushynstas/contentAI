import 'server-only';

const dictionaries = {
  uk: {
    common: () => import('../../public/locales/uk/common.json').then((module) => module.default),
    auth: () => import('../../public/locales/uk/auth/common.json').then((module) => module.default),
    subscription: () => import('../../public/locales/uk/subscription/common.json').then((module) => module.default),
    profile: () => import('../../public/locales/uk/profile/common.json').then((module) => module.default),
  },
  en: {
    common: () => import('../../public/locales/en/common.json').then((module) => module.default),
    auth: () => import('../../public/locales/en/auth/common.json').then((module) => module.default),
    subscription: () => import('../../public/locales/en/subscription/common.json').then((module) => module.default),
    profile: () => import('../../public/locales/en/profile/common.json').then((module) => module.default),
  },
};

export const getDictionary = async (locale, namespace = 'common') => {
  if (!dictionaries[locale] || !dictionaries[locale][namespace]) {
    console.warn(`Dictionary for locale "${locale}" and namespace "${namespace}" not found, falling back to default`);
    return dictionaries['uk']['common']();
  }
  return dictionaries[locale][namespace]();
};

// Для зворотної сумісності
export const getLegacyDictionary = async (locale) => {
  const common = await dictionaries[locale].common();
  const auth = await dictionaries[locale].auth();
  const subscription = await dictionaries[locale].subscription();
  const profile = await dictionaries[locale].profile();
  
  return {
    ...common,
    auth,
    subscription,
    profile
  };
};
