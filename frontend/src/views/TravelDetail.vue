<template>
  <main class="app-page">
    <div class="ink-wash"></div>
    <header class="detail-toolbar">
      <van-button round icon="arrow-left" aria-label="返回" @click="router.back()" />
      <strong>旅行手账</strong>
      <span aria-hidden="true"></span>
    </header>
    <van-skeleton v-if="loading" title :row="8" />
    <TravelHandAccount v-else-if="record" :record="record" />
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { showToast } from 'vant'
import { useRoute, useRouter } from 'vue-router'
import TravelHandAccount from '../components/TravelHandAccount.vue'
import { getTravel } from '../services/api'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const record = ref(null)

onMounted(async () => {
  try {
    const { data } = await getTravel(route.params.id)
    record.value = data
  } catch (error) {
    showToast(error?.response?.data?.detail || '读取手账失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-toolbar {
  position: relative;
  z-index: 5;
  display: grid;
  grid-template-columns: 44px 1fr 44px;
  align-items: center;
  min-height: 58px;
  margin-bottom: 12px;
  color: #153f58;
}

.detail-toolbar strong {
  font-size: 18px;
  text-align: center;
}

.detail-toolbar :deep(.van-button) {
  width: 42px;
  height: 42px;
  border: 1px solid rgba(190, 160, 120, 0.28);
  color: #153f58;
  background: rgba(255, 250, 241, 0.94);
  box-shadow: 0 5px 14px rgba(72, 55, 38, 0.12);
}
</style>
