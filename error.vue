<template>
  <div
    class="postpress-coming-soon"
    :class="{
      'postpress-coming-soon--generic': !isComingSoon,
    }"
  >
    <div class="postpress-coming-soon__inner">
      <p class="postpress-coming-soon__badge">
        {{ isComingSoon ? 'Preview' : 'Oops' }}
      </p>
      <h1 class="postpress-coming-soon__title">
        {{ isComingSoon ? 'Something new is on the way.' : 'We hit a snag.' }}
      </h1>
      <p class="postpress-coming-soon__lead">
        <span v-if="isComingSoon">
          This section of the College Chronicle is in production. Check back soon for fresh reporting, or head to the homepage to keep exploring.
        </span>
        <span v-else>
          {{ props.error?.message || 'An unexpected error occurred. Please return home and try again.' }}
        </span>
      </p>
      <div class="postpress-coming-soon__actions">
        <button type="button" class="postpress-coming-soon__button" @click="handleBack">
          Back to Homepage
        </button>
      </div>
      <p v-if="!isComingSoon && props.error?.statusCode" class="postpress-coming-soon__code">
        Error code {{ props.error.statusCode }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { NuxtError } from '#app'

// Block developer tools
useBlockDevTools()

const props = defineProps<{ error: NuxtError }>()
const isComingSoon = computed(() => [404, 410].includes(Number(props.error?.statusCode ?? 0)))

useHead(() => ({
  title: isComingSoon.value
    ? 'Coming Soon - The College Chronicle'
    : 'Error - The College Chronicle',
}))

const handleBack = () => {
  clearError({ redirect: '/' })
}
</script>
