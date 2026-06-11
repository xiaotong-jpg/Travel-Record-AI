<template>
  <main class="app-page">
    <h1 class="page-title">回忆</h1>
    <p class="page-subtitle">按时间倒序收纳每一页旅程，像慢慢翻开一本数字旅行手账。</p>

    <van-pull-refresh v-model="refreshing" @refresh="loadRecords">
      <section v-if="records.length" class="memory-list">
        <article v-for="item in records" :key="item.id" class="soft-card memory-card" @click="goDetail(item.id)">
          <p class="card-meta">{{ item.place }} · {{ item.travel_date }}</p>
          <h2 class="card-title">{{ item.title }}</h2>
          <div class="tag-row">
            <span v-for="tag in item.mood_tags?.slice(0, 4)" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <p class="card-content">{{ summary(item.content) }}</p>
        </article>
      </section>
      <section v-else class="soft-card empty-state">这里还很安静。生成第一篇旅行日志后，它会出现在这里。</section>
    </van-pull-refresh>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import { listTravels } from '../services/api'

const router = useRouter()
const records = ref([])
const refreshing = ref(false)

function summary(text = '') {
  return text.replace(/\s+/g, ' ').slice(0, 110) + (text.length > 110 ? '...' : '')
}

function goDetail(id) {
  router.push(`/travel/${id}`)
}

async function loadRecords() {
  try {
    const { data } = await listTravels()
    records.value = data
  } catch (error) {
    showToast(error?.response?.data?.detail || '读取回忆失败')
  } finally {
    refreshing.value = false
  }
}

onMounted(loadRecords)
</script>

<style scoped>
.memory-list {
  display: grid;
  gap: 12px;
}

.memory-card {
  cursor: pointer;
}
</style>
