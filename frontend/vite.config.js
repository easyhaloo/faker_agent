import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: true,
    // 优化热重载性能
    hmr: {
      overlay: true,
      timeout: 30000,
      clientPort: 5173
    },
    // 文件系统优化
    watch: {
      usePolling: false,
      interval: 1000
    },
    // 正确配置SPA路由，解决404问题
    historyApiFallback: true,
    // 禁用清屏以获得更好的开发体验
    clearScreen: false
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