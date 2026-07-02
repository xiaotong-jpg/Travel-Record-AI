import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true
      }
    }
  }
})
