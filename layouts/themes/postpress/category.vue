<template>
  <div class="postpress-shell">
    <SiteHeader :brand="brand" :nav="navItems" />

    <main class="postpress-main">
      <div class="postpress-container">
        <SectionHeading :title="title" kicker="Category" />
        <div class="postpress-rail postpress-rail--list">
          <ArticleCard
            v-for="item in stories"
            :key="item._id"
            :doc="item"
          />
        </div>
      </div>
    </main>

    <SiteFooter :brand="brand" :links="footerLinks" />
  </div>
</template>

<script setup lang="ts">
// Block developer tools
useBlockDevTools()

const props = defineProps<{
  category: string
}>()

const config = useAppConfig()
const brand = computed(() => ({
  name: config.name ?? 'PostPress News',
  tagline: config.tagline ?? config.description,
}))
const navItems = computed(() => config.navigation ?? [])
const footerLinks = computed(() => config.footerLinks ?? [])

const title = computed(() =>
  props.category
    .split(/[\s-]+/)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' '),
)

const { data } = await useAsyncData(
  `postpress-category-${props.category}`,
  async () => {
    return queryContent('')
      .where({
        draft: { $ne: true },
        listed: { $ne: false },
        categories: { $in: [props.category] },
      })
      .sort({ date: -1 })
      .find()
  },
)

const stories = computed(() => data.value ?? [])
</script>
