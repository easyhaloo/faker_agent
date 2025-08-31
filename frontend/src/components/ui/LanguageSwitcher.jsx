import { useState } from 'react';
import { useI18n, LANGUAGES } from '../../i18n/index.jsx';
import { Button } from './button';
import { Globe } from 'lucide-react';

/**
 * 语言切换组件
 * 
 * 允许用户在可用语言之间切换
 */
const LanguageSwitcher = () => {
  const { language, changeLanguage } = useI18n();
  const [isOpen, setIsOpen] = useState(false);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleLanguageChange = (lang) => {
    changeLanguage(lang);
    setIsOpen(false);
  };

  // 语言显示名称
  const languageNames = {
    [LANGUAGES.EN]: 'English',
    [LANGUAGES.ZH]: '中文'
  };

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        className="flex items-center"
        onClick={toggleDropdown}
        aria-label="Change language"
      >
        <Globe size={16} className="mr-2" />
        {languageNames[language] || language}
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-40 bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
          <div className="py-1">
            {Object.values(LANGUAGES).map((lang) => (
              <button
                key={lang}
                className={`block w-full text-left px-4 py-2 text-sm ${
                  language === lang
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                onClick={() => handleLanguageChange(lang)}
              >
                {languageNames[lang] || lang}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LanguageSwitcher;