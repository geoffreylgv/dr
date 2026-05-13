import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
  },
  server: {
    proxy: {
      '/api': 'http://localhost:5050',
      '/ws': { target: 'ws://localhost:5050', ws: true },
    },
  },
})
