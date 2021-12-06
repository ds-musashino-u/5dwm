import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        entryFileNames: "[name].js",
        manualChunks: undefined,
        assetFileNames: "assets/[name].[ext]",
      },
    },
    cssCodeSplit: false,
    chunkSizeWarningLimit: 60000,
  },
  plugins: [vue()]
})
