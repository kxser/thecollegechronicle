<template>
  <div class="postpress-shell">
    <SiteHeader :brand="brand" :nav="navItems" />

    <main class="postpress-main">
      <div class="postpress-container postpress-article">
        <article v-if="doc">
          <template v-if="showDocHeader">
            <p v-if="doc.categories?.length" class="postpress-kicker">
              {{ doc.categories[0] }}
            </p>
            <h1 class="postpress-article-headline">
              {{ doc.title }}
            </h1>
            <p v-if="doc.description" class="postpress-article-subhead">
              {{ doc.description }}
            </p>
            <p
              v-if="formattedDate || writerNames.length"
              class="postpress-article-meta"
            >
              <span v-if="formattedDate">{{ formattedDate }}</span>
              <span v-if="writerNames.length">
                <span v-if="formattedDate"> · </span>
                By {{ writerList }}
              </span>
            </p>
          </template>
          <ContentRenderer
            v-if="doc"
            id="postpress-article"
            :value="doc"
            :class="[
              'postpress-article-body',
              { 'postpress-article-body--no-header': !showDocHeader },
            ]"
          />
        </article>

        <section v-if="relatedStories.length" class="postpress-related postpress-section">
          <SectionHeading title="More Coverage" kicker="Recommended" />
          <div class="postpress-rail postpress-rail--list">
            <ArticleCard
              v-for="item in relatedStories"
              :key="item._id"
              :doc="item"
            />
          </div>
        </section>
      </div>
    </main>

    <SiteFooter :brand="brand" :links="footerLinks" />
  </div>
</template>

<script setup lang="ts">
// Block developer tools
useBlockDevTools()

const props = defineProps<{
  doc?: Record<string, any>
}>()

const config = useAppConfig()
const brand = computed(() => ({
  name: config.name ?? 'PostPress News',
  tagline: config.tagline ?? config.description,
}))
const navItems = computed(() => config.navigation ?? [])
const footerLinks = computed(() => config.footerLinks ?? [])
const showDocHeader = computed(() => props.doc?.showHeader ?? true)

const formattedDate = computed(() => {
  if (!props.doc?.date) {
    return ''
  }
  const parsed = new Date(String(props.doc.date))
  if (Number.isNaN(parsed.valueOf())) {
    return ''
  }
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(parsed)
})

const writerNames = computed<string[]>(() => {
  const raw =
    props.doc?.writers ??
    props.doc?.writer ??
    props.doc?.author ??
    props.doc?.authors

  if (!raw) {
    return []
  }

  const list = Array.isArray(raw) ? raw : [raw]

  return list
    .map((entry) =>
      typeof entry === 'string' ? entry.trim() : '',
    )
    .filter((entry): entry is string => Boolean(entry))
})

const writerList = computed(() => writerNames.value.join(', '))

const { data } = await useAsyncData(
  `postpress-related-${props.doc?._path ?? 'none'}`,
  async () => {
    if (!props.doc?.categories?.length) {
      return []
    }

    return queryContent('')
      .where({
        draft: { $ne: true },
        listed: { $ne: false },
        categories: { $in: props.doc.categories },
        _path: { $ne: props.doc._path },
      })
      .sort({ date: -1 })
      .limit(4)
      .find()
  },
)

const relatedStories = computed(() => data.value ?? [])
</script>
