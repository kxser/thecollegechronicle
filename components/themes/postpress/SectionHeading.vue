<template>
  <header class="postpress-section-heading">
    <p v-if="kicker" class="postpress-section-kicker">
      {{ kicker }}
    </p>
    <h2 class="postpress-section-title">
      {{ title }}
    </h2>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  kicker?: string
}>()
</script>
