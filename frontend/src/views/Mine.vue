<template>
  <main class="app-page">
    <h1 class="page-title">我的</h1>
    <p class="page-subtitle">这里会慢慢收纳你的年度足迹、旅行偏好和 AI 陪伴记录。</p>

    <section class="soft-card profile-card">
      <div>
        <p class="card-meta">年度旅行总结</p>
        <h2 class="card-title">把这一年的远方整理成一段话</h2>
        <p class="card-content">AI 会读取已保存的旅行日志，生成一段温柔克制的年度旅行回望。</p>
      </div>
      <van-button type="primary" class="primary-btn summary-btn" :loading="loading" loading-text="正在生成" @click="loadSummary">生成总结</van-button>
    </section>

    <section v-if="summary" class="soft-card summary-card">
      <p class="card-meta">年度回望</p>
      <p class="summary-text">{{ summary }}</p>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { getYearSummary } from '../services/api'

const loading = ref(false)
const summary = ref('')

async function loadSummary() {
  loading.value = true
  try {
    const { data } = await getYearSummary()
    summary.value = data.summary
    showToast('年度总结已生成')
  } catch (error) {
    showToast(error?.response?.data?.detail || '年度总结生成失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-card {
  display: grid;
  gap: 14px;
}

.summary-btn {
  width: 100%;
}

.summary-card {
  margin-top: 16px;
}

.summary-text {
  margin: 8px 0 0;
  color: #4d4239;
  font-size: 15px;
  line-height: 1.9;
  white-space: pre-line;
}
</style>
