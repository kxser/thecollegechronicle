<template>
  <ul class="postpress-paper-copy__list">
    <li
      v-for="issue in issues"
      :key="issue.href"
      class="postpress-paper-copy__item"
    >
      <div class="postpress-paper-copy__meta">
        <span class="postpress-paper-copy__issue">{{ issue.title }}</span>
        <span class="postpress-paper-copy__date">{{ issue.date }}</span>
      </div>
      <NuxtLink
        v-if="issue.href"
        class="postpress-paper-copy__action"
        :to="issue.href"
      >
        Download PDF
      </NuxtLink>
    </li>
  </ul>
</template>

<script setup lang="ts">
interface PaperIssue {
  title: string
  date: string
  href: string
}

const props = defineProps<{ issues: PaperIssue[] }>()
</script>
