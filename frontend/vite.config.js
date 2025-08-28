import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    // 正确配置SPA路由，解决404问题
    historyApiFallback: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      input: {
        main: './index.html'
      },
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'zustand'],
          utils: ['axios']
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  // 确保静态资源正确处理
  publicDir: 'public'
});