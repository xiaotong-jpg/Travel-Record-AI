<template>
  <main class="app-page">
    <h1 class="page-title">回忆</h1>
    <p class="page-subtitle">按时间倒序收纳每一页旅程，像慢慢翻开一本数字旅行手账。</p>

    <section class="soft-card year-entry" @click="router.push('/year-review')">
      <div>
        <p class="card-meta">年度总结</p>
        <h2>这一年，你的足迹</h2>
        <span>查看气泡地图式旅行回顾</span>
      </div>
      <van-icon name="arrow" />
    </section>

    <van-pull-refresh v-model="refreshing" @refresh="loadRecords">
      <section v-if="records.length" class="memory-list">
        <article v-for="item in records" :key="item.id" class="soft-card memory-card" @click="goDetail(item.id)">
          <button class="delete-btn" type="button" aria-label="删除日志" @click.stop="confirmDelete(item)">
            <van-icon name="delete-o" />
          </button>
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
import { showConfirmDialog, showToast } from 'vant'
import { useRouter } from 'vue-router'
import { deleteTravel, listTravels } from '../services/api'

const router = useRouter()
const records = ref([])
const refreshing = ref(false)

function summary(text = '') {
  return text.replace(/\s+/g, ' ').slice(0, 110) + (text.length > 110 ? '...' : '')
}

function goDetail(id) {
  router.push(`/travel/${id}`)
}

async function confirmDelete(item) {
  try {
    await showConfirmDialog({
      title: '删除日志',
      message: `确定删除「${item.title}」吗？删除后无法在列表中恢复。`,
      confirmButtonText: '删除',
      confirmButtonColor: '#b85c46',
      cancelButtonText: '取消'
    })
    await deleteTravel(item.id)
    records.value = records.value.filter((record) => record.id !== item.id)
    showToast('已删除')
  } catch (error) {
    if (error === 'cancel') return
    showToast(error?.response?.data?.detail || '删除失败')
  }
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
.year-entry {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
  cursor: pointer;
}

.year-entry h2 {
  margin: 4px 0 6px;
  color: #123f58;
  font-size: 20px;
}

.year-entry span {
  color: #6f6257;
  font-size: 13px;
}

.year-entry .van-icon {
  color: #55777d;
  font-size: 20px;
}

.memory-list {
  display: grid;
  gap: 12px;
}

.memory-card {
  cursor: pointer;
  padding-right: 52px;
}

.delete-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid rgba(184, 92, 70, 0.24);
  border-radius: 50%;
  color: #b85c46;
  background: rgba(255, 250, 241, 0.78);
  box-shadow: 0 6px 16px rgba(83, 67, 49, 0.08);
}

.delete-btn .van-icon {
  font-size: 17px;
}

.delete-btn:active {
  transform: scale(0.96);
}
</style>
