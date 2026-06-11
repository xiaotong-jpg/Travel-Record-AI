<template>
  <main class="app-page">
    <div class="ink-wash"></div>
    <van-nav-bar title="旅行手账" left-arrow fixed placeholder safe-area-inset-top @click-left="router.back()" />
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
