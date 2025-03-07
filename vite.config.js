import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { quasar } from '@quasar/vite-plugin'


export default defineConfig({
  plugins: [
    vue(),
    quasar()
  ],
});