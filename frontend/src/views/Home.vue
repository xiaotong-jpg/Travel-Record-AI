<template>
  <main class="app-page home-page">
    <div class="ink-wash"></div>
    <AppHeader
      title="AI 旅行记忆助手"
      subtitle="把今天的路线、照片和片刻心情，整理成可回看的旅行手账。"
    />

    <section class="hero-panel">
      <div>
        <p class="hero-kicker">{{ greeting }}</p>
        <h2>{{ heroTitle }}</h2>
        <p>{{ heroText }}</p>
      </div>
      <van-button round icon="plus" type="primary" @click="router.push('/chat-generate')">
        开始记录
      </van-button>
    </section>

    <section class="action-grid">
      <button v-for="item in actions" :key="item.title" type="button" @click="router.push(item.to)">
        <van-icon :name="item.icon" />
        <strong>{{ item.title }}</strong>
        <span>{{ item.desc }}</span>
      </button>
    </section>

    <section class="soft-card insight-card">
      <div class="section-head">
        <div>
          <p class="card-meta">今日灵感</p>
          <h2>给下一页手账的开头</h2>
        </div>
        <van-button size="mini" plain hairline color="#55777d" @click="refreshPrompt">换一句</van-button>
      </div>
      <p class="prompt-text">{{ currentPrompt }}</p>
    </section>

    <section class="stats-grid">
      <div class="soft-card stat-card">
        <van-icon name="location-o" />
        <strong>{{ cityCount }}</strong>
        <span>城市</span>
      </div>
      <div class="soft-card stat-card">
        <van-icon name="notes-o" />
        <strong>{{ records.length }}</strong>
        <span>日志</span>
      </div>
      <div class="soft-card stat-card">
        <van-icon name="photograph" />
        <strong>{{ photoCount }}</strong>
        <span>照片</span>
      </div>
    </section>

    <section class="soft-card next-card">
      <p class="card-meta">AI 下一步</p>
      <h2>{{ nextTitle }}</h2>
      <p>{{ nextText }}</p>
      <div class="next-actions">
        <van-button size="small" plain hairline color="#55777d" @click="router.push('/recommend')">
          查附近推荐
        </van-button>
        <van-button size="small" plain hairline color="#55777d" @click="router.push('/year-review')">
          看年度足迹
        </van-button>
      </div>
    </section>
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
const promptIndex = ref(0)

const prompts = [
  '今天有没有一个画面，值得被贴进手账里？',
  '把路线交给脚步，把细节交给 AI 慢慢整理。',
  '如果只留下一句话，你想把今天写成什么？',
  '上传几张照片，让这段旅程有自己的版式。'
]

const actions = [
  { title: '聊天生成', desc: '边聊边整理', icon: 'chat-o', to: '/chat-generate' },
  { title: '附近推荐', desc: '定位找下一站', icon: 'guide-o', to: '/recommend' },
  { title: '年度足迹', desc: '气泡地图回顾', icon: 'flower-o', to: '/year-review' },
  { title: '回忆库', desc: '查看全部日志', icon: 'notes-o', to: '/memory' }
]

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 11) return '早安，适合出发'
  if (hour < 18) return '午后，适合慢走'
  return '晚上，适合回看'
})

const heroTitle = computed(() => (records.value.length ? '继续收藏今天的风景' : '从第一段旅行记忆开始'))
const heroText = computed(() => (
  records.value.length
    ? `已经保存 ${records.value.length} 篇日志，今天可以继续生成新的手账或查看附近推荐。`
    : '填写地点、心情和照片，AI 会帮你生成一页完整的旅行手账。'
))
const currentPrompt = computed(() => prompts[promptIndex.value % prompts.length])
const cityCount = computed(() => new Set(records.value.map((item) => cityName(item.place))).size)
const photoCount = computed(() => records.value.reduce((sum, item) => sum + (item.image_urls?.length || 0), 0))
const nextTitle = computed(() => (records.value.length >= 3 ? '适合生成年度足迹了' : '先积累几段旅行片刻'))
const nextText = computed(() => (
  records.value.length >= 3
    ? '你的日志已经足够组成一张年度气泡地图，可以看看这一年的路线脉络。'
    : '继续生成几篇手账后，年度总结和个人数据会更完整。'
))

function cityName(place = '') {
  return String(place).split(/[·\s,，、-]/).filter(Boolean)[0] || '未知'
}

function refreshPrompt() {
  promptIndex.value += 1
}

onMounted(async () => {
  try {
    const { data } = await listTravels()
    records.value = data
  } catch (error) {
    showToast(error?.response?.data?.detail || '读取首页数据失败')
  }
})
</script>

<style scoped>
.home-page {
  padding-bottom: 108px;
}

.hero-panel {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 18px;
  min-height: 196px;
  padding: 22px 18px;
  border-radius: 18px;
  color: #173d52;
  background:
    radial-gradient(circle at 82% 18%, rgba(255, 255, 255, 0.78), transparent 22%),
    linear-gradient(135deg, rgba(230, 241, 240, 0.92), rgba(255, 246, 231, 0.92)),
    linear-gradient(145deg, #8fb1b7, #d89a70);
  box-shadow: var(--shadow-card);
}

.hero-panel::after {
  content: "";
  position: absolute;
  right: -28px;
  bottom: -32px;
  width: 140px;
  height: 110px;
  border: 1px solid rgba(18, 75, 102, 0.16);
  border-radius: 50%;
}

.hero-kicker {
  margin: 0 0 8px;
  color: #936b42;
  font-size: 13px;
}

.hero-panel h2 {
  margin: 0;
  font-size: 25px;
  line-height: 1.28;
}

.hero-panel p:last-child {
  margin: 10px 0 0;
  max-width: 270px;
  color: #4d6470;
  line-height: 1.7;
}

.hero-panel .van-button {
  justify-self: start;
  border: 0;
  background: #124b66;
}

.action-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 14px;
}

.action-grid button {
  display: grid;
  gap: 6px;
  min-height: 104px;
  padding: 14px;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  color: #173d52;
  text-align: left;
  background: rgba(255, 250, 241, 0.76);
  box-shadow: var(--shadow-soft);
}

.action-grid .van-icon {
  font-size: 24px;
  color: #55777d;
}

.action-grid strong {
  font-size: 16px;
}

.action-grid span {
  color: #7b6f66;
  font-size: 12px;
}

.insight-card {
  margin-top: 14px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.section-head h2 {
  margin: 2px 0 0;
  color: #173d52;
  font-size: 18px;
}

.prompt-text {
  margin: 14px 0 0;
  padding-left: 12px;
  border-left: 3px solid rgba(202, 164, 106, 0.55);
  color: #4f463f;
  font-size: 16px;
  line-height: 1.8;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 14px;
}

.stat-card {
  display: grid;
  justify-items: center;
  gap: 6px;
  padding: 14px 8px;
  text-align: center;
}

.stat-card .van-icon {
  color: #8f8072;
  font-size: 22px;
}

.stat-card strong {
  color: #173d52;
  font-family: Georgia, serif;
  font-size: 24px;
}

.stat-card span {
  color: #7d7168;
  font-size: 12px;
}

.next-card {
  margin-top: 14px;
}

.next-card h2 {
  margin: 4px 0 8px;
  color: #173d52;
  font-size: 18px;
}

.next-card p {
  margin: 0;
  color: #5a514a;
  line-height: 1.75;
}

.next-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}
</style>
