<template>
  <main class="app-page chat-page">
    <div class="ink-wash"></div>
    <AppHeader
      title="AI 旅行搭子"
      subtitle="不用一次写完整，我会像旅行搭子一样慢慢问，把这段回忆整理成手账。"
    />

    <section class="chat-board">
      <transition-group name="fade-rise">
        <div v-for="(item, index) in messages" :key="index" class="bubble-row" :class="item.role">
          <div class="bubble">{{ item.content }}</div>
        </div>
      </transition-group>
    </section>

    <section class="soft-card upload-card">
      <div class="upload-head">
        <div>
          <h3>旅行照片</h3>
          <p>上传 1-9 张，生成后会贴进手账长页。</p>
        </div>
        <span>{{ uploadFiles.length }}/9</span>
      </div>
      <van-uploader
        v-model="uploadFiles"
        multiple
        :max-count="9"
        :after-read="afterRead"
        upload-icon="photograph"
      />
    </section>

    <section v-if="Object.keys(travelInfo).length" class="soft-card info-card">
      <p class="card-meta">已整理的信息</p>
      <div class="tag-row">
        <span v-for="(value, key) in travelInfo" :key="key" class="tag">{{ fieldName(key) }}：{{ value || '跳过' }}</span>
      </div>
    </section>

    <div class="chat-input">
      <van-field
        v-model="input"
        placeholder="慢慢说，我在听..."
        rows="1"
        autosize
        type="textarea"
        @keyup.enter="send"
      />
      <van-button round type="primary" :loading="sending" loading-text="思考中" @click="send">发送</van-button>
      <van-button round class="generate-btn" :loading="generating" @click="generate">生成手账</van-button>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import { generateTravelFromChat, sendChatMessage } from '../services/api'

const router = useRouter()
const sessionId = ref('')
const input = ref('')
const sending = ref(false)
const generating = ref(false)
const travelInfo = ref({})
const uploadFiles = ref([])
const rawFiles = ref([])
const messages = ref([
  { role: 'assistant', content: '这次旅行去了哪里呀？我来帮你把这段回忆整理成旅行日志。' }
])

function afterRead(file) {
  const files = Array.isArray(file) ? file : [file]
  rawFiles.value = uploadFiles.value.map((item) => item.file).filter(Boolean).slice(0, 9)
  files.forEach(() => showToast('照片已贴进待整理的回忆里'))
}

function fieldName(key) {
  const map = { place: '地点', memory: '记忆', companion: '同行', mood: '心情', quote: '一句话', style: '风格', travel_date: '时间' }
  return map[key] || key
}

async function send() {
  const text = input.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  sending.value = true
  try {
    const { data } = await sendChatMessage({ session_id: sessionId.value || undefined, message: text })
    sessionId.value = data.session_id
    travelInfo.value = data.travel_info
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch (error) {
    showToast(error?.response?.data?.detail || '搭子刚才走神了，请再说一次')
  } finally {
    sending.value = false
  }
}

async function generate() {
  if (!sessionId.value) {
    showToast('先和 AI 搭子聊一句吧')
    return
  }
  generating.value = true
  try {
    rawFiles.value = uploadFiles.value.map((item) => item.file).filter(Boolean).slice(0, 9)
    const { data } = await generateTravelFromChat({
      sessionId: sessionId.value,
      travelInfo: travelInfo.value,
      images: rawFiles.value
    })
    showToast('旅行手账已生成')
    router.push(`/travel/${data.id}`)
  } catch (error) {
    showToast(error?.response?.data?.detail || '生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.chat-page {
  padding-bottom: 150px;
}

.chat-board {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 12px;
  margin-bottom: 14px;
}

.bubble-row {
  display: flex;
}

.bubble-row.user {
  justify-content: flex-end;
}

.bubble {
  max-width: 78%;
  padding: 12px 13px;
  border-radius: 16px;
  color: #4f443b;
  line-height: 1.7;
  background: rgba(255, 250, 241, 0.86);
  border: 1px solid var(--color-line);
  box-shadow: var(--shadow-soft);
}

.user .bubble {
  color: #fffaf1;
  background: linear-gradient(135deg, var(--color-primary-mist-blue), var(--color-soft-green));
}

.upload-card,
.info-card {
  margin-top: 12px;
}

.upload-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.upload-head h3 {
  margin: 0 0 4px;
  font-size: 16px;
}

.upload-head p {
  margin: 0;
  color: var(--color-muted);
  font-size: 12px;
}

.chat-input {
  position: fixed;
  left: 50%;
  bottom: 58px;
  z-index: 5;
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 8px;
  width: min(430px, 100vw);
  padding: 10px 12px calc(10px + env(safe-area-inset-bottom));
  transform: translateX(-50%);
  background: rgba(255, 250, 241, 0.92);
  border-top: 1px solid var(--color-line);
  backdrop-filter: blur(16px);
}

.generate-btn {
  color: #6b5031;
  border-color: rgba(202, 164, 106, 0.35);
  background: rgba(202, 164, 106, 0.18);
}
</style>
