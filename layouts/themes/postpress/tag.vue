<template>
  <div class="postpress-shell">
    <SiteHeader :brand="brand" :nav="navItems" />

    <main class="postpress-main">
      <div class="postpress-container">
        <SectionHeading :title="title" kicker="Tag" />
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
  tag: string
}>()

const config = useAppConfig()
const brand = computed(() => ({
  name: config.name ?? 'PostPress News',
  tagline: config.tagline ?? config.description,
}))
const navItems = computed(() => config.navigation ?? [])
const footerLinks = computed(() => config.footerLinks ?? [])

const title = computed(() => `#${props.tag}`)

const { data } = await useAsyncData(
  `postpress-tag-${props.tag}`,
  async () => {
    return queryContent('')
      .where({
        draft: { $ne: true },
        listed: { $ne: false },
        tags: { $in: [props.tag] },
      })
      .sort({ date: -1 })
      .find()
  },
)

const stories = computed(() => data.value ?? [])
</script>
