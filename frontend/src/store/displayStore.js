import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useDisplayStore = create(
  persist(
    (set, get) => ({
      // 显示设置
      displaySettings: {
        fontSize: 'medium',     // small | medium | large
        layout: 'comfortable',  // comfortable | compact
        animation: true,        // 是否启用动画
        compactMode: false,     // 是否启用紧凑模式
        theme: 'system',        // light | dark | system
      },

      // 更新显示设置
      updateDisplaySettings: (newSettings) => {
        set((state) => ({
          displaySettings: {
            ...state.displaySettings,
            ...newSettings
          }
        }));
      },

      // 重置显示设置
      resetDisplaySettings: () => {
        set({
          displaySettings: {
            fontSize: 'medium',
            layout: 'comfortable',
            animation: true,
            compactMode: false,
            theme: 'system',
          }
        });
      },

      // 应用字体大小到DOM
      applyFontSize: () => {
        const { fontSize } = get().displaySettings;
        const root = document.documentElement;
        
        // 移除所有字体大小类
        root.classList.remove('text-small', 'text-medium', 'text-large');
        
        // 添加当前字体大小类
        root.classList.add(`text-${fontSize}`);
        
        // 也可以通过CSS变量设置
        const sizeMap = {
          small: '14px',
          medium: '16px',
          large: '18px'
        };
        
        root.style.setProperty('--base-font-size', sizeMap[fontSize] || sizeMap.medium);
      },

      // 应用布局模式到DOM
      applyLayout: () => {
        const { layout } = get().displaySettings;
        const root = document.documentElement;
        
        // 移除所有布局类
        root.classList.remove('layout-comfortable', 'layout-compact');
        
        // 添加当前布局类
        root.classList.add(`layout-${layout}`);
      },

      // 应用动画设置到DOM
      applyAnimation: () => {
        const { animation } = get().displaySettings;
        const root = document.documentElement;
        
        if (animation) {
          root.classList.remove('no-animation');
        } else {
          root.classList.add('no-animation');
        }
      },

      // 应用紧凑模式到DOM
      applyCompactMode: () => {
        const { compactMode } = get().displaySettings;
        const root = document.documentElement;
        
        if (compactMode) {
          root.classList.add('compact-mode');
        } else {
          root.classList.remove('compact-mode');
        }
      },

      // 应用主题设置到DOM
      applyTheme: () => {
        const { theme } = get().displaySettings;
        const root = document.documentElement;
        
        // 清除现有主题类
        root.classList.remove('light', 'dark');
        
        if (theme === 'system') {
          // 根据系统偏好设置主题
          const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          root.classList.add(isDark ? 'dark' : 'light');
          localStorage.removeItem('theme');
        } else {
          // 应用指定主题
          root.classList.add(theme);
          localStorage.setItem('theme', theme);
        }
      },

      // 应用所有显示设置
      applyAllDisplaySettings: () => {
        get().applyFontSize();
        get().applyLayout();
        get().applyAnimation();
        get().applyCompactMode();
        get().applyTheme();
      }
    }),
    {
      name: 'display-settings-storage',
      partialize: (state) => ({ 
        displaySettings: state.displaySettings
      }),
    }
  )
);