import 'server-only';

const dictionaries = {
  uk: () => import('../../public/locales/uk/common.json').then((module) => module.default),
  en: () => import('../../public/locales/en/common.json').then((module) => module.default),
};

export const getDictionary = async (locale) => {
  return dictionaries[locale]();
};
