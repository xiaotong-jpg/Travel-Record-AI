<template>
  <main class="app-page">
    <h1 class="page-title">生成旅行日志</h1>
    <p class="page-subtitle">写下地点、心情和片刻记忆，AI 会帮你整理成一页温柔的旅行手账。</p>

    <section class="soft-card form-card">
      <van-form @submit="submit">
        <van-cell-group inset>
          <van-field v-model="form.place" name="place" label="旅行地点" placeholder="例如：杭州西湖" :rules="[{ required: true, message: '请填写旅行地点' }]" />
          <van-field v-model="form.travel_date" name="travel_date" label="旅行时间" placeholder="选择日期" readonly is-link @click="showDate = true" :rules="[{ required: true, message: '请选择旅行时间' }]" />
          <van-field v-model="form.companion" name="companion" label="同行人" placeholder="朋友、家人、一个人..." />
          <van-field v-model="form.mood" name="mood" label="当天心情" placeholder="松弛、开心、治愈..." />
          <van-field v-model="form.memory" name="memory" label="最深印象" type="textarea" rows="3" autosize placeholder="那天最想记住的一件事" :rules="[{ required: true, message: '请写下印象最深的事情' }]" />
          <van-field v-model="form.quote" name="quote" label="一句话" placeholder="想留在这页手账里的话" />
          <van-field v-model="form.style" name="style" label="日志风格" placeholder="选择风格" readonly is-link @click="showStyle = true" />
        </van-cell-group>

        <van-button block native-type="submit" type="primary" class="primary-btn" :loading="loading" loading-text="AI 正在整理回忆">生成旅行日志</van-button>
      </van-form>
    </section>

    <section v-if="result" class="soft-card result-card">
      <p class="card-meta">{{ result.place }} · {{ result.travel_date }} · {{ result.style }}</p>
      <h2 class="card-title">{{ result.title }}</h2>
      <p class="card-content">{{ result.content }}</p>
      <div class="tag-row">
        <span v-for="tag in result.mood_tags" :key="tag" class="tag">{{ tag }}</span>
      </div>
      <div class="divider"></div>
      <p class="card-meta">地点气质</p>
      <p class="card-content">{{ result.location_desc }}</p>
      <p class="card-meta">贴纸标签</p>
      <div class="tag-row">
        <span v-for="tag in result.stickers" :key="tag" class="tag">{{ tag }}</span>
      </div>
      <p class="card-meta share-label">分享文案</p>
      <p class="share-text">{{ result.share_text }}</p>
    </section>

    <van-popup v-model:show="showDate" position="bottom">
      <van-date-picker title="选择旅行时间" :min-date="minDate" :max-date="maxDate" @confirm="onDateConfirm" @cancel="showDate = false" />
    </van-popup>
    <van-popup v-model:show="showStyle" position="bottom">
      <van-picker :columns="styles" title="选择日志风格" @confirm="onStyleConfirm" @cancel="showStyle = false" />
    </van-popup>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { showToast } from 'vant'
import { generateTravel } from '../services/api'

const styles = ['手账风', '明信片风', '朋友圈风', '小红书风', '电影旁白风', '简洁记录风']
const today = new Date()
const minDate = new Date(2000, 0, 1)
const maxDate = new Date(today.getFullYear(), today.getMonth(), today.getDate())

const form = reactive({
  place: '',
  travel_date: '',
  companion: '',
  mood: '',
  memory: '',
  quote: '',
  style: '手账风'
})

const showDate = ref(false)
const showStyle = ref(false)
const loading = ref(false)
const result = ref(null)

function formatDate(values) {
  const [year, month, day] = values.selectedValues
  return `${year}-${month}-${day}`
}

function onDateConfirm(values) {
  form.travel_date = formatDate(values)
  showDate.value = false
}

function onStyleConfirm({ selectedValues }) {
  form.style = selectedValues[0]
  showStyle.value = false
}

async function submit() {
  loading.value = true
  try {
    const { data } = await generateTravel({ ...form })
    result.value = data
    showToast('旅行日志已生成')
  } catch (error) {
    showToast(error?.response?.data?.detail || '生成失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.result-card {
  margin-top: 16px;
}

.divider {
  height: 1px;
  margin: 14px 0;
  background: var(--line);
}

.share-label {
  margin-top: 14px;
}

.share-text {
  margin: 8px 0 0;
  padding: 12px;
  border-left: 3px solid rgba(123, 143, 116, 0.55);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.44);
  color: #5f5146;
  line-height: 1.75;
}
</style>
