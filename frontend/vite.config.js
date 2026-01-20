import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { quasar } from '@quasar/vite-plugin';
import path from 'path';

export default defineConfig({
  plugins: [
    vue(),
    quasar(),
  ],
  define: {
    __BASE__URL__: JSON.stringify('http://localhost:8002'),
  },
  resolve: {
    alias: {
      '@assets': path.join(__dirname, './assets'),
      '@components': path.join(__dirname, './components'),
      '@pages': path.join(__dirname, './pages'),
      '@api': path.join(__dirname, './providers'),
			'@store': path.join(__dirname, './store'),
			'@config': path.join(__dirname, './config'),
			'@composables': path.join(__dirname, './composables'),
    }
  },
});