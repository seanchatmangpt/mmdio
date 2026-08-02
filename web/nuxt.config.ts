export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/ui'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_MMDIO_API_BASE ?? 'http://localhost:8000'
    }
  },
  app: {
    head: {
      title: 'mmdio — Mermaid as Universal IO',
      meta: [
        {
          name: 'description',
          content: 'A receipt-aware visual control plane for machine-operated computing.'
        }
      ]
    }
  }
})
