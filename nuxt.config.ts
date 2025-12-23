// https://nuxt.com/docs/api/configuration/nuxt-config
import * as sass from 'sass'

export default defineNuxtConfig({
  compatibilityDate: "2025-12-23",
  nitro: {
    preset: "cloudflare_module",
    cloudflare: {
      deployConfig: true,
      nodeCompat: true
  }},
  devtools: { enabled: true },
  css: ['~/assets/styles/themes/postpress.css'],
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          implementation: sass,
        } as any,
      },
    },
  },
  app: {
    head: {
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'shortcut icon', href: '/favicon.ico' },
        { rel: 'apple-touch-icon', href: '/metucollegelogo.png' },
        { rel: 'icon', type: 'image/png', href: '/metucollegelogo.png' },
      ],
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'format-detection', content: 'telephone=no' },
      ],
    },
  },
  components: [
    {
      path: '~/components/themes/postpress',
      pathPrefix: false,
    },
  ],
  plugins: ['~/plugins/consola-box'],
  modules: ['@nuxtjs/sitemap', '@nuxtjs/robots'],
  extends: ['@bloggrify/core'],
  site: {
    url: 'https://thecollegechronicle.org',
    name: 'The College Chronicle',
    indexable: true,
  },
  sitemap: {
    credits: false,
    strictNuxtContentPaths: true,
    defaults: {
      changefreq: 'weekly',
      priority: 0.7,
    },
  },
  robots: {
    rules: [
      {
        userAgent: '*',
        allow: '/',
      },
    ],
    sitemap: ['https://thecollegechronicle.org/sitemap.xml'],
  } as any,
})
