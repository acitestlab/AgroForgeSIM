// vite.config.ts
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'), // use "@/..." imports
      },
    },
    server: {
      host: true,        // listens on 0.0.0.0
      port: 5173,
      strictPort: true,
      cors: true,
      open: false,

      // Optional: proxy to your FastAPI when calling relative "/api/*"
      // If you prefer absolute URLs via VITE_API_BASE, you can remove this.
      proxy: env.VITE_API_BASE
        ? {
            '/api': {
              target: env.VITE_API_BASE, // e.g. http://localhost:8000
              changeOrigin: true,
              ws: true,
              rewrite: (p) => p.replace(/^\/api/, ''),
            },
          }
        : undefined,
    },
    preview: {
      host: true,
      port: 5173,
    },
    build: {
      target: 'es2020',
      sourcemap: true,
      outDir: 'dist',
      emptyOutDir: true,
    },
    optimizeDeps: {
      include: ['leaflet'], // pre-bundle leaflet for faster dev
    },
  }
})
