import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { quasar } from '@quasar/vite-plugin';
import path from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    vue(),
    quasar(),
		react()
  ],
  define: {
    __BASE__URL__: JSON.stringify('http://localhost:8002'),
  },
  resolve: {
    alias: {
      '@assets': path.join(__dirname, '/frontend/assets'),
      '@components': path.join(__dirname, '/frontend/components'),
      '@pages': path.join(__dirname, '/frontend/pages')
    }
  },
});