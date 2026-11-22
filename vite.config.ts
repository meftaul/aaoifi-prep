import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  // Served from https://meftaul.github.io/aaoifi-prep/
  base: '/aaoifi-prep/',
  plugins: [react()],
})
