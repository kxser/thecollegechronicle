<template>
  <div class="postpress-shell">
    <SiteHeader :brand="brand" :nav="navItems" />

    <main class="postpress-main">
      <div class="postpress-container">
        <!-- Debug info (remove in production) -->
        <div v-if="articles.length === 0" style="padding: 2rem; color: #999; text-align: center; font-family: monospace;">
          <p>No articles found after filtering.</p>
          <p>Total items fetched: {{ (allArticles || []).length }}</p>
          <p>After filtering: {{ articles.length }}</p>
          <details v-if="allArticles && allArticles.length > 0" style="margin-top: 1rem; text-align: left;">
            <summary>Show raw data</summary>
            <pre style="font-size: 0.8rem; overflow: auto;">{{ JSON.stringify(allArticles[0], null, 2) }}</pre>
          </details>
        </div>

        <!-- Hero Section -->
        <section v-if="heroArticle" class="nyt-hero-section">
          <article class="nyt-hero-article">
            <NuxtLink :to="heroArticle._path" class="nyt-hero-link">
              <p v-if="heroArticle.categories?.[0]" class="nyt-hero-category">
                {{ heroArticle.categories[0] }}
              </p>
              <h1 class="nyt-hero-headline">
                {{ heroArticle.title }}
              </h1>
              <p v-if="heroArticle.description" class="nyt-hero-description">
                {{ heroArticle.description }}
              </p>
            </NuxtLink>
          </article>
        </section>

        <!-- Top Stories Grid -->
        <section v-if="topStories.length" class="nyt-top-stories">
          <div class="nyt-grid-primary">
            <article
              v-for="article in topStories"
              :key="article._id"
              class="nyt-story-card"
            >
              <NuxtLink :to="article._path" class="nyt-story-link">
                <p v-if="article.categories?.[0]" class="nyt-story-category">
                  {{ article.categories[0] }}
                </p>
                <h2 class="nyt-story-headline">
                  {{ article.title }}
                </h2>
                <p v-if="article.description" class="nyt-story-description">
                  {{ article.description }}
                </p>
                <p class="nyt-story-meta">
                  {{ formatDate(article.date) }}
                </p>
              </NuxtLink>
            </article>
          </div>
        </section>

        <!-- Opinion Section -->
        <section v-if="opinionArticles.length" class="nyt-section nyt-opinion-section">
          <div class="nyt-section-header">
            <h2 class="nyt-section-title">Opinion</h2>
          </div>
          <div class="nyt-opinion-grid">
            <article
              v-for="article in opinionArticles"
              :key="article._id"
              class="nyt-opinion-card"
            >
              <NuxtLink :to="article._path" class="nyt-opinion-link">
                <div v-if="article.writers?.[0]" class="nyt-opinion-author">
                  {{ article.writers[0] }}
                </div>
                <h3 class="nyt-opinion-headline">
                  {{ article.title }}
                </h3>
                <p v-if="article.description" class="nyt-opinion-description">
                  {{ article.description }}
                </p>
              </NuxtLink>
            </article>
          </div>
        </section>

        <!-- Mixed Content Grid -->
        <section v-if="middleContent.length" class="nyt-section nyt-mixed-section">
          <div class="nyt-mixed-grid">
            <article
              v-for="(article, idx) in middleContent"
              :key="article._id"
              :class="['nyt-mixed-card', getMixedCardClass(idx)]"
            >
              <NuxtLink :to="article._path" class="nyt-mixed-link">
                <p v-if="article.categories?.[0]" class="nyt-mixed-category">
                  {{ article.categories[0] }}
                </p>
                <h3 class="nyt-mixed-headline">
                  {{ article.title }}
                </h3>
                <p v-if="article.description" class="nyt-mixed-description">
                  {{ article.description }}
                </p>
                <p class="nyt-mixed-meta">
                  {{ formatDate(article.date) }}
                </p>
              </NuxtLink>
            </article>
          </div>
        </section>

        <!-- More News List -->
        <section v-if="moreNews.length" class="nyt-section nyt-more-news">
          <div class="nyt-section-header">
            <h2 class="nyt-section-title">More News</h2>
          </div>
          <div class="nyt-news-list">
            <article
              v-for="article in moreNews"
              :key="article._id"
              class="nyt-news-item"
            >
              <NuxtLink :to="article._path" class="nyt-news-link">
                <h4 class="nyt-news-headline">
                  {{ article.title }}
                </h4>
                <p v-if="article.description" class="nyt-news-description">
                  {{ article.description }}
                </p>
                <p class="nyt-news-meta">
                  <span v-if="article.date">{{ formatDate(article.date) }}</span>
                  <span v-if="article.categories?.[0]" class="nyt-news-category">
                    · {{ article.categories[0] }}
                  </span>
                </p>
              </NuxtLink>
            </article>
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

const config = useAppConfig()
const brand = computed(() => ({
  name: config.name ?? 'PostPress News',
  tagline: config.tagline ?? config.description,
}))
const navItems = computed(() => config.navigation ?? [])
const footerLinks = computed(() => config.footerLinks ?? [])

// Fetch all articles, sorted by date
const { data: allArticles } = await useAsyncData('home-all-articles', async () => {
  return await queryContent('/')
    .where({
      _path: { $ne: '/index' }
    })
    .sort({ date: -1 })
    .find()
})

const articles = computed(() => {
  const raw = allArticles.value ?? []
  // Filter out non-article pages and ensure required fields exist
  return raw.filter(a => 
    a._path && 
    a._path !== '/index' &&
    !a._path.startsWith('/staff') &&
    a._path !== '/paper-copy' &&
    a.title &&
    a.date &&
    a.listed !== false &&
    a.draft !== true
  )
})

console.log('Articles loaded:', allArticles.value?.length, 'Filtered:', articles.value.length)

// Hero article (most recent)
const heroArticle = computed(() => articles.value[0] || null)

// Top stories (next 6 articles, mixed categories)
const topStories = computed(() => articles.value.slice(1, 7))

// Opinion articles (up to 4)
const opinionArticles = computed(() => {
  return articles.value
    .filter(a => a.categories?.includes('opinion'))
    .slice(0, 4)
})

// Middle content (mixed categories, excluding hero, top stories, and displayed opinions)
const middleContent = computed(() => {
  const usedIds = new Set([
    heroArticle.value?._id,
    ...topStories.value.map(a => a._id),
    ...opinionArticles.value.map(a => a._id),
  ].filter(Boolean))
  
  return articles.value
    .filter(a => !usedIds.has(a._id))
    .slice(0, 9)
})

// More news list
const moreNews = computed(() => {
  const usedIds = new Set([
    heroArticle.value?._id,
    ...topStories.value.map(a => a._id),
    ...opinionArticles.value.map(a => a._id),
    ...middleContent.value.map(a => a._id),
  ].filter(Boolean))
  
  return articles.value
    .filter(a => !usedIds.has(a._id))
    .slice(0, 10)
})

const getMixedCardClass = (index: number) => {
  // Create varied sizing like NYT
  if (index === 0) return 'nyt-mixed-card--large'
  if (index === 3 || index === 6) return 'nyt-mixed-card--medium'
  return 'nyt-mixed-card--small'
}

const formatDate = (value?: string) => {
  if (!value) return ''
  const dateValue = new Date(String(value))
  if (Number.isNaN(dateValue.valueOf())) return ''
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(dateValue)
}
</script>
