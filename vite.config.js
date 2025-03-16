import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { quasar } from '@quasar/vite-plugin'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    quasar()
  ],
  resolve: {
    alias: {
      '@assets': path.join(__dirname, '/frontend/assets'),
      '@components': path.join(__dirname, '/frontend/components'),
      '@pages': path.join(__dirname, '/frontend/pages')
    }
  }
});