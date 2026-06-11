<template>
  <main class="app-page">
    <div class="ink-wash"></div>
    <AppHeader title="下一站推荐" subtitle="根据你所在的位置、偏好和已去过的地方，给下一段路一点温柔建议。" />

    <section class="soft-card location-card">
      <p class="card-meta">当前位置</p>
      <van-field v-model="form.city" label="城市" placeholder="例如：北京" />
      <van-field v-model="form.current_place" label="地点" placeholder="例如：什刹海" />
      <van-button size="small" plain hairline color="#55777d" @click="locate">获取当前位置</van-button>
    </section>

    <section class="soft-card preference-card">
      <p class="card-meta">今天想要的旅行质感</p>
      <div class="pref-grid">
        <button
          v-for="item in preferenceOptions"
          :key="item"
          type="button"
          :class="{ active: form.preferences.includes(item) }"
          @click="togglePreference(item)"
        >
          {{ item }}
        </button>
      </div>
      <van-field v-model="visitedText" label="已去过" placeholder="用逗号分隔，例如：鼓楼、南锣鼓巷" />
      <van-button block type="primary" class="primary-btn" :loading="loading" @click="submit">智能推荐下一站</van-button>
    </section>

    <section v-if="result" class="result-area">
      <div class="soft-card postcard">
        <p class="card-meta">明信片式建议</p>
        <h2 class="card-title">{{ result.postcard_text }}</h2>
        <p class="card-content">{{ result.summary }}</p>
      </div>
      <RecommendationCard v-for="item in result.recommendations" :key="item.name" :item="item" />
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { showToast } from 'vant'
import AppHeader from '../components/AppHeader.vue'
import RecommendationCard from '../components/RecommendationCard.vue'
import { recommendNearby } from '../services/api'

const preferenceOptions = ['拍照打卡', '美食', '小众安静', '文化古迹', '夜景', '亲子', '购物', '自然风景']
const visitedText = ref('')
const loading = ref(false)
const result = ref(null)
const form = reactive({
  city: '北京',
  current_place: '什刹海',
  latitude: null,
  longitude: null,
  preferences: ['小众安静', '文化古迹'],
  visited_places: []
})

function togglePreference(item) {
  const index = form.preferences.indexOf(item)
  if (index >= 0) form.preferences.splice(index, 1)
  else form.preferences.push(item)
}

function locate() {
  if (!navigator.geolocation) {
    showToast('当前浏览器不支持定位，可手动输入地点')
    return
  }
  navigator.geolocation.getCurrentPosition(
    (position) => {
      form.latitude = position.coords.latitude
      form.longitude = position.coords.longitude
      showToast('位置已记录，可以继续补充城市和地点')
    },
    () => showToast('定位失败，请手动输入当前位置')
  )
}

async function submit() {
  loading.value = true
  try {
    form.visited_places = visitedText.value.split(/[,，]/).map((item) => item.trim()).filter(Boolean)
    const { data } = await recommendNearby({ ...form })
    result.value = data
    showToast(data.fallback ? '已生成兜底推荐' : '下一站建议已整理好')
  } catch (error) {
    showToast(error?.response?.data?.detail || '推荐失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.location-card,
.preference-card {
  margin-bottom: 14px;
}

.pref-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin: 12px 0;
}

.pref-grid button {
  min-height: 38px;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  color: #695a4d;
  background: rgba(255, 250, 241, 0.64);
}

.pref-grid button.active {
  color: #fffaf1;
  border-color: transparent;
  background: linear-gradient(135deg, var(--color-primary-mist-blue), var(--color-soft-green));
}

.result-area {
  display: grid;
  gap: 12px;
}
</style>
