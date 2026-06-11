<template>
  <main class="app-page">
    <div class="ink-wash"></div>
    <AppHeader title="AI 旅行记忆助手" subtitle="把路过的风、停下来的光，整理成一页可以回看的旅行手账。" />

    <section class="soft-card postcard">
      <div class="card-meta">往日此刻</div>
      <h2 class="card-title">{{ featured?.title || '今天适合翻一页旧回忆' }}</h2>
      <p class="card-content">{{ featuredText }}</p>
      <div class="tag-row">
        <span class="tag">{{ featured?.place || '未命名远方' }}</span>
        <span class="tag">{{ featured?.travel_date || '等待第一段旅程' }}</span>
      </div>
    </section>

    <div class="section-title">
      <span>最近生成</span>
      <van-button size="mini" plain hairline color="#55777d" to="/chat-generate">找搭子聊聊</van-button>
    </div>

    <section v-if="records.length" class="recent-list">
      <article v-for="item in records.slice(0, 3)" :key="item.id" class="soft-card memory-card" @click="goDetail(item.id)">
        <p class="card-meta">{{ item.place }} · {{ item.travel_date }} · {{ item.style }}</p>
        <h3 class="card-title">{{ item.title }}</h3>
        <p class="card-content">{{ summary(item.content) }}</p>
        <div class="tag-row">
          <span v-for="tag in item.mood_tags?.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </article>
    </section>
    <section v-else class="soft-card empty-state">还没有旅行日志。去生成页，把今天的记忆交给 AI 轻轻整理。</section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import { listTravels } from '../services/api'

const router = useRouter()
const records = ref([])
const featured = computed(() => records.value[0])
const featuredText = computed(() => {
  if (!featured.value) return '第一张明信片还空着，等你把地点、心情和一句话写给它。'
  return featured.value.share_text || summary(featured.value.content)
})

function summary(text = '') {
  return text.replace(/\s+/g, ' ').slice(0, 86) + (text.length > 86 ? '...' : '')
}

function goDetail(id) {
  router.push(`/travel/${id}`)
}

onMounted(async () => {
  try {
    const { data } = await listTravels()
    records.value = data
  } catch (error) {
    showToast(error?.response?.data?.detail || '读取旅行记录失败')
  }
})
</script>

<style scoped>
.recent-list {
  display: grid;
  gap: 12px;
}

.memory-card {
  cursor: pointer;
}
</style>
