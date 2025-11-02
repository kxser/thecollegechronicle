<template>
  <article class="postpress-article-card">
    <NuxtLink :to="doc?._path ?? '#'" class="postpress-card-title">
      {{ doc?.title }}
    </NuxtLink>
    <p v-if="doc?.description" class="postpress-card-description">
      {{ doc.description }}
    </p>
    <p class="postpress-card-meta">
      <span v-if="formattedDate">
        {{ formattedDate }}
      </span>
      <span v-if="doc?.categories?.length">
        <span v-if="formattedDate"> · </span>
        {{ doc.categories.join(', ') }}
      </span>
    </p>
  </article>
</template>

<script setup lang="ts">
const props = defineProps<{
  doc: Record<string, any>
}>()

const formattedDate = computed(() => {
  if (!props.doc?.date) {
    return ''
  }
  const value = new Date(String(props.doc.date))
  if (Number.isNaN(value.valueOf())) {
    return ''
  }
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(value)
})
</script>
