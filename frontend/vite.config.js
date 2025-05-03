import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/chat': 'http://localhost:8000',
      '/query': 'http://localhost:8000',
      '/sessions': 'http://localhost:8000',
    },
  },
});
