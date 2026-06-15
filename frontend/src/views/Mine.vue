<template>
  <main class="app-page mine-page">
    <div class="ink-wash"></div>
    <section class="profile-hero">
      <div class="avatar">旅</div>
      <div>
        <p>旅行手账创作者</p>
        <h1>我的旅行工作台</h1>
        <span>{{ profileLine }}</span>
      </div>
    </section>

    <section class="dashboard-grid">
      <div class="soft-card metric-card">
        <strong>{{ records.length }}</strong>
        <span>日志总数</span>
      </div>
      <div class="soft-card metric-card">
        <strong>{{ styleCount }}</strong>
        <span>使用风格</span>
      </div>
      <div class="soft-card metric-card">
        <strong>{{ photoCount }}</strong>
        <span>照片素材</span>
      </div>
    </section>

    <section class="soft-card preference-card">
      <div class="section-head">
        <div>
          <p class="card-meta">偏好画像</p>
          <h2>AI 已理解的旅行质感</h2>
        </div>
        <van-icon name="setting-o" />
      </div>
      <div class="tag-row">
        <span v-for="tag in preferenceTags" :key="tag" class="tag">{{ tag }}</span>
      </div>
    </section>

    <section class="tool-list">
      <button v-for="item in tools" :key="item.title" type="button" class="soft-card tool-card" @click="router.push(item.to)">
        <van-icon :name="item.icon" />
        <div>
          <strong>{{ item.title }}</strong>
          <span>{{ item.desc }}</span>
        </div>
        <van-icon name="arrow" />
      </button>
    </section>

    <section class="soft-card settings-card">
      <p class="card-meta">应用设置</p>
      <div class="setting-row">
        <div>
          <strong>AI 生成模式</strong>
          <span>使用后端配置的大模型 API</span>
        </div>
        <van-tag plain type="success">已启用</van-tag>
      </div>
      <div class="setting-row">
        <div>
          <strong>本地数据</strong>
          <span>日志保存在本机数据库和上传目录</span>
        </div>
        <van-tag plain>SQLite</van-tag>
      </div>
      <div class="setting-row">
        <div>
          <strong>隐私提示</strong>
          <span>定位仅用于附近推荐，请按需授权</span>
        </div>
        <van-tag plain type="warning">可控</van-tag>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import { listTravels } from '../services/api'

const router = useRouter()
const records = ref([])

const tools = [
  { title: '年度足迹海报', desc: '生成你的旅行气泡地图', icon: 'flower-o', to: '/year-review' },
  { title: '手账生成器', desc: '和 AI 聊天生成日志', icon: 'chat-o', to: '/chat-generate' },
  { title: '下一站推荐', desc: '根据当前位置找附近灵感', icon: 'guide-o', to: '/recommend' }
]

const photoCount = computed(() => records.value.reduce((sum, item) => sum + (item.image_urls?.length || 0), 0))
const styleCount = computed(() => new Set(records.value.map((item) => item.style).filter(Boolean)).size)
const profileLine = computed(() => (
  records.value.length
    ? `已整理 ${records.value.length} 段旅程，继续把风景收进手账。`
    : '还没有旅行日志，先生成第一篇手账。'
))
const preferenceTags = computed(() => {
  const tags = records.value.flatMap((item) => [...(item.mood_tags || []), item.style].filter(Boolean))
  const unique = [...new Set(tags)].slice(0, 8)
  return unique.length ? unique : ['手账风', '慢旅行', '拍照记录', '小众安静']
})

onMounted(async () => {
  try {
    const { data } = await listTravels()
    records.value = data
  } catch (error) {
    showToast(error?.response?.data?.detail || '读取个人数据失败')
  }
})
</script>

<style scoped>
.mine-page {
  padding-bottom: 108px;
}

.profile-hero {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  border-radius: 18px;
  background:
    linear-gradient(135deg, rgba(255, 252, 246, 0.92), rgba(232, 242, 239, 0.8)),
    radial-gradient(circle at 86% 22%, rgba(216, 154, 112, 0.22), transparent 30%);
  border: 1px solid var(--color-line);
  box-shadow: var(--shadow-card);
}

.avatar {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 18px;
  color: #fffaf1;
  background: #124b66;
  font-family: Georgia, "Songti SC", serif;
  font-size: 26px;
  font-weight: 800;
}

.profile-hero p {
  margin: 0 0 4px;
  color: #9a7145;
  font-size: 12px;
}

.profile-hero h1 {
  margin: 0;
  color: #173d52;
  font-size: 23px;
  line-height: 1.3;
}

.profile-hero span {
  display: block;
  margin-top: 6px;
  color: #6f6257;
  font-size: 13px;
  line-height: 1.55;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 14px;
}

.metric-card {
  display: grid;
  justify-items: center;
  gap: 6px;
  padding: 14px 8px;
  text-align: center;
}

.metric-card strong {
  color: #173d52;
  font-family: Georgia, serif;
  font-size: 25px;
}

.metric-card span {
  color: #7d7168;
  font-size: 12px;
}

.preference-card {
  margin-top: 14px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.section-head h2 {
  margin: 2px 0 0;
  color: #173d52;
  font-size: 18px;
}

.section-head .van-icon {
  color: #55777d;
  font-size: 22px;
}

.tool-list {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.tool-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  width: 100%;
  border-radius: 14px;
  color: inherit;
  text-align: left;
}

.tool-card > .van-icon:first-child {
  color: #55777d;
  font-size: 24px;
}

.tool-card > .van-icon:last-child {
  color: #9b8d81;
}

.tool-card strong {
  display: block;
  color: #173d52;
  font-size: 16px;
}

.tool-card span {
  display: block;
  margin-top: 4px;
  color: #7d7168;
  font-size: 12px;
}

.settings-card {
  display: grid;
  gap: 14px;
  margin-top: 14px;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-line);
}

.setting-row:first-of-type {
  padding-top: 0;
  border-top: 0;
}

.setting-row strong {
  display: block;
  color: #3f352d;
  font-size: 14px;
}

.setting-row span {
  display: block;
  margin-top: 4px;
  color: #7d7168;
  font-size: 12px;
}
</style>
