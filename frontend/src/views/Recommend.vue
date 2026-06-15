<template>
  <main class="app-page">
    <div class="ink-wash"></div>
    <AppHeader
      title="下一站推荐"
      subtitle="获取当前位置后，由 AI 分析你所在的城市和附近可去的景点，再整理成下一站建议。"
    />

    <section class="soft-card location-card">
      <div class="section-head">
        <p class="card-meta">当前位置</p>
        <span v-if="locationStatus" class="location-status">{{ locationStatus }}</span>
      </div>
      <van-field v-model="form.city" label="城市" placeholder="定位后自动填写，也可手动输入" />
      <van-field v-model="form.current_place" label="地点" placeholder="定位后自动分析附近区域/地标" />
      <div v-if="coordinateText" class="coordinate-line">
        <van-icon name="location-o" />
        <span>{{ coordinateText }}</span>
      </div>
      <p v-if="locationDescription" class="location-desc">{{ locationDescription }}</p>
      <van-button
        size="small"
        plain
        hairline
        color="#55777d"
        :loading="locating"
        @click="locate"
      >
        获取当前位置并推荐
      </van-button>
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
      <van-button block type="primary" class="primary-btn" :loading="loading" @click="submit">
        智能推荐下一站
      </van-button>
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
import { computed, reactive, ref } from 'vue'
import { showToast } from 'vant'
import AppHeader from '../components/AppHeader.vue'
import RecommendationCard from '../components/RecommendationCard.vue'
import { recommendNearby, resolveLocation } from '../services/api'

const preferenceOptions = ['拍照打卡', '美食', '小众安静', '文化古迹', '夜景', '亲子', '购物', '自然风景']
const visitedText = ref('')
const loading = ref(false)
const locating = ref(false)
const locationStatus = ref('')
const locationDescription = ref('')
const result = ref(null)
const form = reactive({
  city: '',
  current_place: '',
  latitude: null,
  longitude: null,
  preferences: ['小众安静', '文化古迹'],
  visited_places: []
})

const coordinateText = computed(() => {
  if (form.latitude == null || form.longitude == null) return ''
  return `坐标：${Number(form.latitude).toFixed(5)}, ${Number(form.longitude).toFixed(5)}`
})

function togglePreference(item) {
  const index = form.preferences.indexOf(item)
  if (index >= 0) form.preferences.splice(index, 1)
  else form.preferences.push(item)
}

function isLocalhost() {
  return ['localhost', '127.0.0.1', '::1'].includes(window.location.hostname)
}

function syncVisitedPlaces() {
  form.visited_places = visitedText.value.split(/[,，、]/).map((item) => item.trim()).filter(Boolean)
}

async function locate() {
  if (!navigator.geolocation) {
    locationStatus.value = '浏览器不支持定位'
    showToast('当前浏览器不支持定位，可手动输入城市和地点')
    return
  }
  if (!window.isSecureContext && !isLocalhost()) {
    locationStatus.value = '需要 HTTPS 或 localhost'
    showToast('浏览器定位需要 HTTPS；请用 localhost/127.0.0.1 打开，或手动输入地点')
    return
  }

  locating.value = true
  locationStatus.value = '正在请求定位权限'
  try {
    if (navigator.permissions?.query) {
      const permission = await navigator.permissions.query({ name: 'geolocation' })
      if (permission.state === 'denied') {
        locationStatus.value = '定位权限已拒绝'
        showToast('请在浏览器地址栏权限设置里允许定位')
        return
      }
    }

    const position = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 12000,
        maximumAge: 60000
      })
    })
    form.latitude = position.coords.latitude
    form.longitude = position.coords.longitude
    locationStatus.value = 'AI 正在分析位置'
    syncVisitedPlaces()

    const { data } = await resolveLocation({
      latitude: form.latitude,
      longitude: form.longitude,
      preferences: form.preferences,
      visited_places: form.visited_places
    })
    form.city = data.city || form.city
    form.current_place = data.current_place || form.current_place
    locationDescription.value = data.description || ''
    result.value = data.recommendations?.length ? data : result.value
    locationStatus.value = data.fallback ? '已记录坐标，需手动补充位置' : 'AI 已识别位置'
    showToast(data.fallback ? '已记录坐标，可补充城市后再推荐' : '已根据当前位置生成推荐')
  } catch (error) {
    const messageMap = {
      1: '定位权限被拒绝',
      2: '暂时无法获取位置',
      3: '定位超时'
    }
    locationStatus.value = messageMap[error?.code] || '位置分析失败'
    showToast(`${locationStatus.value}，可手动输入当前位置`)
  } finally {
    locating.value = false
  }
}

async function submit() {
  loading.value = true
  try {
    syncVisitedPlaces()
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

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.location-status {
  color: #31566a;
  font-size: 12px;
}

.coordinate-line {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 8px 0 10px;
  color: #4b5d5f;
  font-size: 12px;
}

.location-desc {
  margin: 0 0 12px;
  color: #5d5147;
  font-size: 13px;
  line-height: 1.6;
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
  color: #4c4239;
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
