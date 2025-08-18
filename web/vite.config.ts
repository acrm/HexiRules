import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/session': 'http://127.0.0.1:8000',
      '/world': 'http://127.0.0.1:8000',
      '/worlds': 'http://127.0.0.1:8000',
      '/history': 'http://127.0.0.1:8000',
      '/step': 'http://127.0.0.1:8000'
    }
  },
  build: {
    outDir: 'dist'
  }
})
