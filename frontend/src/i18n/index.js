import { en } from './en';
import { zh } from './zh';
import { createContext, useContext, useState, useEffect } from 'react';

// 可用语言列表
export const LANGUAGES = {
  EN: 'en',
  ZH: 'zh'
};

// 语言包
export const translations = {
  [LANGUAGES.EN]: en,
  [LANGUAGES.ZH]: zh
};

// 创建国际化上下文
export const I18nContext = createContext({
  language: LANGUAGES.EN,
  t: (key) => key,
  changeLanguage: () => {},
  translations: {}
});

// 自定义钩子用于访问国际化功能
export const useI18n = () => useContext(I18nContext);

// 国际化提供者组件
export const I18nProvider = ({ children, defaultLanguage = LANGUAGES.EN }) => {
  // 尝试从 localStorage 读取用户语言偏好
  const getUserLanguage = () => {
    try {
      const savedLang = localStorage.getItem('preferredLanguage');
      if (savedLang && Object.values(LANGUAGES).includes(savedLang)) {
        return savedLang;
      }
      
      // 尝试检测浏览器语言
      const browserLang = navigator.language.split('-')[0];
      return browserLang === 'zh' ? LANGUAGES.ZH : defaultLanguage;
    } catch (e) {
      return defaultLanguage;
    }
  };

  const [language, setLanguage] = useState(getUserLanguage());

  // 翻译函数
  const t = (key) => {
    const keys = key.split('.');
    let value = translations[language];
    
    for (let k of keys) {
      if (value === undefined) return key;
      value = value[k];
    }
    
    return value || key;
  };

  // 切换语言
  const changeLanguage = (lang) => {
    if (Object.values(LANGUAGES).includes(lang)) {
      setLanguage(lang);
      try {
        localStorage.setItem('preferredLanguage', lang);
      } catch (e) {
        console.error('Failed to save language preference:', e);
      }
    }
  };

  // 更新 document.title 和 html lang 属性
  useEffect(() => {
    document.documentElement.lang = language;
    document.title = t('common.welcome');
  }, [language]);

  const value = {
    language,
    t,
    changeLanguage,
    translations: translations[language]
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};

export default { I18nProvider, useI18n, LANGUAGES };