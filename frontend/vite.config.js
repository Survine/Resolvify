import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/shops': 'http://localhost:8000',
      '/employees': 'http://localhost:8000',
      '/teams': 'http://localhost:8000',
      '/roles': 'http://localhost:8000',
      '/chat/shops': 'http://localhost:8000',
      '/chat/sessions': 'http://localhost:8000',
      '/chat/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
      '/customers': 'http://localhost:8000',
      '/permissions': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})
