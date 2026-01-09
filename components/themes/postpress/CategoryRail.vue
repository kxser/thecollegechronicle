<template>
  <div v-if="docs.length" :class="['postpress-rail', variantClass]">
    <div v-if="variant === 'feature' && lead" class="postpress-rail-feature">
      <p v-if="lead.categories?.[0]" class="postpress-kicker">
        {{ lead.categories[0] }}
      </p>
      <NuxtLink :to="lead._path" class="postpress-lead-headline">
        {{ lead.title }}
      </NuxtLink>
      <p v-if="lead.description" class="postpress-lead-summary">
        {{ lead.description }}
      </p>
      <p class="postpress-meta">
        {{ formatDate(lead.date) }}
      </p>
    </div>
    <div
      :class="[
        'postpress-rail-list',
        { 'postpress-rail-list--feature': variant === 'feature' },
      ]"
    >
      <ArticleCard
        v-for="item in remainder"
        :key="item._id"
        :doc="item"
      />
    </div>
  </div>
  <p v-else class="postpress-empty-state">
    No stories published yet.
  </p>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    category?: string
    tag?: string
    limit?: number
    variant?: 'feature' | 'list'
    offset?: number
    excludePaths?: string[]
  }>(),
  {
    limit: 4,
    variant: 'feature',
    offset: 0,
    excludePaths: () => [],
  },
)

const asyncKey = `postpress-rail-${props.category ?? props.tag ?? 'all'}-${props.offset}-${props.limit}-${props.variant}`

const { data } = await useAsyncData(asyncKey, async () => {
  const filter: Record<string, any> = {
    draft: { $ne: true },
    listed: { $ne: false },
  }

  if (props.category) {
    filter.categories = { $in: [props.category] }
  }
  if (props.tag) {
    filter.tags = { $in: [props.tag] }
  }
  if (props.excludePaths.length) {
    filter._path = { $nin: props.excludePaths }
  }

  let builder = queryContent('')
    .where(filter)
    .sort({ date: -1 })

  if (props.offset) {
    builder = builder.skip(props.offset)
  }

  builder = builder.limit(props.limit)

  return builder.find()
})

const docs = computed(() => data.value ?? [])
const lead = computed(() => (props.variant === 'feature' ? docs.value?.[0] : null))
const remainder = computed(() => {
  if (!docs.value?.length) {
    return []
  }

  if (props.variant === 'feature') {
    return docs.value.slice(1)
  }

  return docs.value
})

const variantClass = computed(() =>
  props.variant === 'feature' ? 'postpress-rail--feature' : 'postpress-rail--list',
)

const formatDate = (value?: string) => {
  if (!value) {
    return ''
  }
  const dateValue = new Date(String(value))
  if (Number.isNaN(dateValue.valueOf())) {
    return ''
  }
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(dateValue)
}
</script>
