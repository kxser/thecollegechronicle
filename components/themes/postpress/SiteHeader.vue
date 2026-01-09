<template>
  <header class="postpress-masthead">
    <div class="postpress-container postpress-masthead-inner">
      <NuxtLink to="/" class="postpress-masthead-title">
        {{ brand.name }}
      </NuxtLink>
      <p v-if="brand.tagline" class="postpress-masthead-tagline">
        {{ brand.tagline }}
      </p>
      <p class="postpress-masthead-date">
        {{ dateline }}
      </p>
    </div>
    <nav v-if="nav.length" class="postpress-nav">
      <div class="postpress-container">
        <ul class="postpress-nav-list">
          <li
            v-for="item in nav"
            :key="item.label"
            class="postpress-nav-item"
            :class="{ 
              'postpress-nav-item--divider': item.label === 'News',
              'postpress-nav-item--apply': item.label === 'Apply Now'
            }"
          >
            <a
              v-if="item.external"
              :href="item.to"
              class="postpress-nav-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ item.label }}
            </a>
            <NuxtLink v-else :to="item.to" class="postpress-nav-link">
              {{ item.label }}
            </NuxtLink>
          </li>
        </ul>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    brand: { name: string; tagline?: string };
    nav?: { label: string; to: string; external?: boolean }[];
  }>(),
  {
    nav: () => [],
  },
)

const dateline = computed(() => {
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date())
})
</script>
