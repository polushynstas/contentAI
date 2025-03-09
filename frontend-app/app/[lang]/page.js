import { getDictionary } from './dictionaries';

export async function generateStaticParams() {
  return [{ lang: 'uk' }, { lang: 'en' }];
}

export default async function Home({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang;
  
  const dict = await getDictionary(lang);
  
  const translations = {
    uk: {
      title: 'Генеруйте ідеї для контенту швидко та легко',
      subtitle: 'ContentAI допомагає створювати ідеї для соціальних мереж, блогів та відео на основі ваших параметрів',
      getStarted: 'Почати',
      features: {
        title: 'Можливості',
        feature1: {
          title: 'Генерація ідей',
          description: 'Отримуйте унікальні ідеї для контенту на основі вашої ніші та аудиторії'
        },
        feature2: {
          title: 'Аналіз трендів',
          description: 'Дізнавайтеся про актуальні тренди у вашій ніші для створення релевантного контенту'
        },
        feature3: {
          title: 'Хештеги',
          description: 'Отримуйте рекомендації щодо хештегів для збільшення охоплення вашого контенту'
        }
      }
    },
    en: {
      title: 'Generate Content Ideas Quickly and Easily',
      subtitle: 'ContentAI helps you create ideas for social media, blogs, and videos based on your parameters',
      getStarted: 'Get Started',
      features: {
        title: 'Features',
        feature1: {
          title: 'Idea Generation',
          description: 'Get unique content ideas based on your niche and audience'
        },
        feature2: {
          title: 'Trend Analysis',
          description: 'Learn about current trends in your niche to create relevant content'
        },
        feature3: {
          title: 'Hashtags',
          description: 'Get hashtag recommendations to increase your content reach'
        }
      }
    }
  };
  
  const t = translations[lang];

  return (
    <div className="flex flex-col items-center">
      <section className="w-full py-12 md:py-24 lg:py-32">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center space-y-4 text-center">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
              {t.title}
            </h1>
            <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl">
              {t.subtitle}
            </p>
            <div className="space-x-4">
              <a
                href={`/${lang}/signup`}
                className="inline-flex h-10 items-center justify-center rounded-md bg-indigo-600 px-8 text-sm font-medium text-white shadow transition-colors hover:bg-indigo-700 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-indigo-700"
              >
                {t.getStarted}
              </a>
            </div>
          </div>
        </div>
      </section>
      
      <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-100">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center space-y-4 text-center">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
              {t.features.title}
            </h2>
            <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-3 lg:gap-12">
              <div className="flex flex-col items-center space-y-2 rounded-lg border p-4">
                <div className="p-2 rounded-full bg-indigo-100">
                  <svg
                    className="h-6 w-6 text-indigo-600"
                    fill="none"
                    height="24"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    width="24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path d="M12 2v4" />
                    <path d="m6.343 6.343 2.83 2.83" />
                    <path d="M2 12h4" />
                    <path d="m6.343 17.657 2.83-2.83" />
                    <path d="M12 18v4" />
                    <path d="m17.657 17.657-2.83-2.83" />
                    <path d="M22 12h-4" />
                    <path d="m17.657 6.343-2.83 2.83" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold">{t.features.feature1.title}</h3>
                <p className="text-sm text-gray-500">
                  {t.features.feature1.description}
                </p>
              </div>
              <div className="flex flex-col items-center space-y-2 rounded-lg border p-4">
                <div className="p-2 rounded-full bg-indigo-100">
                  <svg
                    className="h-6 w-6 text-indigo-600"
                    fill="none"
                    height="24"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    width="24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path d="m3 3 7.07 16.97 2.51-7.39 7.39-2.51L3 3z" />
                    <path d="m13 13 6 6" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold">{t.features.feature2.title}</h3>
                <p className="text-sm text-gray-500">
                  {t.features.feature2.description}
                </p>
              </div>
              <div className="flex flex-col items-center space-y-2 rounded-lg border p-4">
                <div className="p-2 rounded-full bg-indigo-100">
                  <svg
                    className="h-6 w-6 text-indigo-600"
                    fill="none"
                    height="24"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    width="24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold">{t.features.feature3.title}</h3>
                <p className="text-sm text-gray-500">
                  {t.features.feature3.description}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
