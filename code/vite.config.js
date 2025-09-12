import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Base path so assets resolve correctly when served from GitHub Pages at /ai-interviewer/
  // If you deploy to a custom domain or user/organization page root, adjust or remove this.
  base: '/ai-interviewer/'
})
