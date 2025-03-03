import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  root: path.resolve(__dirname, './frontend/public'), // Указываем корневую папку
  build: {
    outDir: path.resolve(__dirname, './frontend/public/js'), // Куда будут собираться файлы
    rollupOptions: {
      input: {
        admin: path.resolve(__dirname, './frontend/src/admin/main.js'), // Точка входа
      },
      output: {
        entryFileNames: `[name].js`,
        chunkFileNames: `[name].js`,
        assetFileNames: `[name].[ext]`,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'), // Алиас для удобства
    },
  },
});