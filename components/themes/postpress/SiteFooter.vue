<template>
  <footer class="postpress-footer">
    <div class="postpress-container postpress-footer-inner">
      <div class="postpress-footer-left">
        <div class="postpress-footer-brand">
          {{ brand.name }}
        </div>
        <p v-if="brand.tagline" class="postpress-footer-tagline">
          {{ brand.tagline }}
        </p>
        <p class="postpress-footer-copy">
          © {{ currentYear }} {{ brand.name }}. All rights reserved.
          <span class="postpress-footer-credit">
            Website created by
            <a href="https://derinaritter.com" target="_blank" rel="noopener">
              Derin Alan Ritter
            </a>
          </span>
        </p>
      </div>
      <div class="postpress-footer-right">
        <div class="postpress-footer-logo-wrap">
          <img
            class="postpress-footer-logo"
            src="/metucollegelogo.png"
            alt="METU College Logo"
            loading="lazy"
          />
        </div>
        <nav v-if="links.length" class="postpress-footer-nav">
          <NuxtLink v-for="item in links" :key="item.label" :to="item.to">
            {{ item.label }}
          </NuxtLink>
        </nav>
      </div>
    </div>
    <p class="postpress-footer-disclaimer">
      The College Chronicle is a monthly magazine covering a wide range of topics, approved by ODTU GV Private Ankara High School and done in accordance with teacher guidelines.
    </p>
  </footer>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    brand: { name: string; tagline?: string };
    links?: { label: string; to: string }[];
  }>(),
  {
    links: () => [],
  },
)

const currentYear = new Date().getFullYear()
</script>
