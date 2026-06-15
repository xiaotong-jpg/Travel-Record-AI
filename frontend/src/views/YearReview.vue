<template>
  <main class="year-review-page">
    <section ref="posterRef" class="year-poster">
      <div class="soft-leaf leaf-left"></div>
      <div class="soft-leaf leaf-right"></div>
      <div class="bird bird-a"></div>
      <div class="bird bird-b"></div>
      <div class="bird bird-c"></div>

      <div class="top-actions no-export">
        <van-button round icon="arrow-left" @click="router.back()" />
        <van-button round icon="share-o" @click="exportImage" />
      </div>

      <header class="hero-copy">
        <h1>这一年，你的足迹</h1>
        <p>{{ reviewYear }} · Year in Review</p>
        <span>每一段旅程，都是人生的珍贵收藏。</span>
        <i></i>
      </header>

      <section v-if="displayRecords.length" class="bubble-field">
        <article
          v-for="(item, index) in displayRecords"
          :key="item.id"
          class="place-bubble"
          :class="`bubble-${index}`"
          type="button"
          @click="goDetail(item.id)"
        >
          <div class="water-ring"></div>
          <div class="bubble-photo" :style="bubbleStyle(item, index)"></div>
          <div class="bubble-glass"></div>
          <div class="bubble-content">
            <h2>{{ bubbleTitle(item, index) }}</h2>
            <p>{{ bubbleSubtitle(item, index) }}</p>
            <div class="bubble-tags">
              <span v-for="tag in bubbleTags(item, index)" :key="tag">#{{ tag }}</span>
            </div>
          </div>
        </article>
      </section>

      <section v-else class="empty-bubbles">
        <h2>还没有年度足迹</h2>
        <p>生成几篇旅行日志后，这里会自动变成你的年度旅行地图。</p>
      </section>

      <section class="travel-data-card">
        <div class="data-title">
          <span></span>
          <h2>{{ reviewYear }} 旅行数据</h2>
          <span></span>
        </div>

        <div class="data-grid">
          <div class="data-item">
            <van-icon name="location" />
            <strong>{{ cityCount }}</strong>
            <p>探索城市</p>
          </div>
          <div class="data-item">
            <van-icon name="guide-o" />
            <strong>{{ stepCount }}</strong>
            <p>步行里程（步）</p>
          </div>
          <div class="data-item">
            <van-icon name="photograph" />
            <strong>{{ photoCount }}</strong>
            <p>拍摄照片</p>
          </div>
          <div class="data-item">
            <van-icon name="like" />
            <strong>{{ records.length }}</strong>
            <p>收藏地点</p>
          </div>
        </div>

        <van-button round block icon="description-o" class="diary-button" @click="router.push('/memory')">
          查看完整旅行日记
        </van-button>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import html2canvas from 'html2canvas'
import { listTravels } from '../services/api'

const router = useRouter()
const records = ref([])
const posterRef = ref(null)
const reviewYear = new Date().getFullYear()

const scenicFallbacks = [
  {
    title: '北京 · 什刹海',
    subtitle: '烟火人间里的慢时光',
    tags: ['古都韵味', '胡同记忆'],
    image: 'linear-gradient(145deg, rgba(205,226,239,.88), rgba(242,228,203,.76)), radial-gradient(circle at 68% 70%, rgba(145,81,45,.52), transparent 28%)'
  },
  {
    title: '云南 · 丽江',
    subtitle: '雪山之下的宁静小城',
    tags: ['治愈风景', '纳西古镇'],
    image: 'linear-gradient(145deg, rgba(211,231,238,.9), rgba(232,244,238,.7)), radial-gradient(circle at 50% 78%, rgba(53,143,166,.55), transparent 34%)'
  },
  {
    title: '福建 · 平潭岛',
    subtitle: '海风治愈的浪漫之地',
    tags: ['蓝色海岸', '追风之旅'],
    image: 'linear-gradient(145deg, rgba(200,225,238,.88), rgba(246,238,216,.72)), radial-gradient(circle at 72% 72%, rgba(93,116,89,.52), transparent 30%)'
  },
  {
    title: '上海 · 外滩',
    subtitle: '繁华与浪漫交织的夜',
    tags: ['都市夜景', '摩都记忆'],
    image: 'linear-gradient(145deg, rgba(210,225,237,.9), rgba(232,219,201,.72)), radial-gradient(circle at 62% 76%, rgba(70,75,118,.58), transparent 30%)'
  },
  {
    title: '美食探索',
    subtitle: '舌尖上的美好时光',
    tags: ['地方美食', '人间烟火'],
    image: 'linear-gradient(145deg, rgba(237,225,203,.9), rgba(219,235,229,.76)), radial-gradient(circle at 58% 74%, rgba(197,151,91,.55), transparent 30%)'
  }
]

const displayRecords = computed(() => {
  const currentYearRecords = records.value.filter((item) => String(item.travel_date || '').startsWith(String(reviewYear)))
  const source = currentYearRecords.length ? currentYearRecords : records.value
  return source.slice(0, 5)
})

const cityCount = computed(() => new Set(records.value.map((item) => cityName(item.place))).size)
const photoCount = computed(() => records.value.reduce((sum, item) => sum + (item.image_urls?.length || 0), 0))
const stepCount = computed(() => (records.value.length * 6820 + cityCount.value * 1846).toLocaleString())

function goDetail(id) {
  router.push(`/travel/${id}`)
}

function cityName(place = '') {
  return String(place).split(/[·\s,，、-]/).filter(Boolean)[0] || '未知城市'
}

function bubbleTitle(item, index) {
  if (!item?.place) return scenicFallbacks[index]?.title || '旅行片刻'
  const parts = String(item.place).split(/[·,，、-]/).map((part) => part.trim()).filter(Boolean)
  if (parts.length >= 2) return `${parts[0]} · ${parts[1]}`
  return item.place
}

function bubbleSubtitle(item, index) {
  return item?.location_desc || item?.share_text || compact(item?.content, 16) || scenicFallbacks[index]?.subtitle || '值得收藏的一段旅程'
}

function compact(text = '', length = 18) {
  return String(text).replace(/\s+/g, '').slice(0, length)
}

function bubbleTags(item, index) {
  const realTags = [...(item?.mood_tags || []), ...(item?.stickers || [])].filter(Boolean).slice(0, 2)
  return realTags.length ? realTags : scenicFallbacks[index]?.tags || ['旅行记忆', '年度收藏']
}

function assetUrl(url) {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('data:')) return url
  if (url.startsWith('/uploads')) return url
  return `/uploads/${url.replace(/^\/+/, '')}`
}

function bubbleStyle(item, index) {
  const uploaded = item?.image_urls?.[0]
  if (uploaded) {
    return {
      backgroundImage: `linear-gradient(180deg, rgba(225,239,246,.18), rgba(245,239,222,.2)), url("${assetUrl(uploaded)}")`
    }
  }
  return { backgroundImage: scenicFallbacks[index % scenicFallbacks.length].image }
}

async function exportImage() {
  if (!posterRef.value) return
  const hidden = posterRef.value.querySelectorAll('.no-export')
  try {
    hidden.forEach((item) => item.classList.add('is-exporting'))
    const canvas = await html2canvas(posterRef.value, {
      backgroundColor: '#f8f1e7',
      scale: 2,
      useCORS: true,
      allowTaint: true,
      scrollY: -window.scrollY
    })
    const link = document.createElement('a')
    link.download = `${reviewYear}-旅行年度总结.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    showToast('年度总结图片已生成')
  } catch (error) {
    showToast('导出失败，请稍后重试')
  } finally {
    hidden.forEach((item) => item.classList.remove('is-exporting'))
  }
}

onMounted(async () => {
  try {
    const { data } = await listTravels()
    records.value = data
  } catch (error) {
    showToast(error?.response?.data?.detail || '读取年度总结失败')
  }
})
</script>

<style scoped>
.year-review-page {
  min-height: 100vh;
  max-width: 430px;
  margin: 0 auto;
  overflow: hidden;
  color: #123f58;
  background: #f8f1e7;
}

.year-poster {
  position: relative;
  min-height: 100vh;
  padding: 76px 24px 24px;
  overflow: hidden;
  background:
    radial-gradient(circle at 12% 6%, rgba(147, 166, 153, 0.16), transparent 26%),
    radial-gradient(circle at 88% 14%, rgba(145, 178, 194, 0.16), transparent 24%),
    radial-gradient(circle at 62% 46%, rgba(211, 190, 146, 0.08), transparent 34%),
    linear-gradient(180deg, #fbf5eb 0%, #f7efe3 100%);
}

.top-actions {
  position: absolute;
  inset: 36px 26px auto;
  z-index: 8;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}

.top-actions :deep(.van-button) {
  width: 48px;
  height: 48px;
  border: 1px solid rgba(211, 191, 162, 0.72);
  color: #164861;
  background: rgba(250, 244, 234, 0.88);
  box-shadow: 0 10px 24px rgba(83, 64, 42, 0.12);
  pointer-events: auto;
}

.hero-copy {
  position: relative;
  z-index: 2;
  margin-left: 66px;
}

.hero-copy h1 {
  margin: 0;
  color: #123f58;
  font-family: Georgia, "Songti SC", serif;
  font-size: 31px;
  font-weight: 800;
  line-height: 1.25;
}

.hero-copy p {
  margin: 9px 0 18px;
  color: #a87545;
  font-family: Georgia, serif;
  font-size: 17px;
  font-style: italic;
}

.hero-copy span {
  display: block;
  color: #657a83;
  font-size: 15px;
  line-height: 1.7;
}

.hero-copy i {
  display: block;
  width: 58px;
  height: 1px;
  margin-top: 20px;
  background: #b6864b;
}

.soft-leaf {
  position: absolute;
  pointer-events: none;
  opacity: 0.36;
}

.soft-leaf::before,
.soft-leaf::after {
  content: "";
  position: absolute;
  border-radius: 60% 0 60% 0;
  background: rgba(111, 139, 125, 0.18);
}

.leaf-left {
  left: -18px;
  top: 4px;
  width: 110px;
  height: 170px;
  transform: rotate(-24deg);
}

.leaf-left::before {
  width: 34px;
  height: 86px;
  left: 18px;
  top: 10px;
}

.leaf-left::after {
  width: 28px;
  height: 72px;
  left: 48px;
  top: 52px;
}

.leaf-right {
  right: -10px;
  top: 468px;
  width: 110px;
  height: 180px;
  transform: rotate(20deg);
}

.leaf-right::before {
  width: 32px;
  height: 82px;
  right: 18px;
  top: 14px;
}

.leaf-right::after {
  width: 28px;
  height: 70px;
  right: 50px;
  top: 62px;
}

.bird {
  position: absolute;
  z-index: 1;
  width: 28px;
  height: 12px;
  border-top: 2px solid rgba(87, 116, 126, 0.42);
  border-radius: 50%;
}

.bird::after {
  content: "";
  position: absolute;
  right: -14px;
  top: -2px;
  width: 28px;
  height: 12px;
  border-top: 2px solid rgba(87, 116, 126, 0.42);
  border-radius: 50%;
  transform: rotate(-16deg);
}

.bird-a {
  right: 66px;
  top: 142px;
  transform: rotate(12deg) scale(0.9);
}

.bird-b {
  right: 104px;
  top: 124px;
  transform: rotate(-8deg) scale(0.72);
}

.bird-c {
  right: 34px;
  top: 104px;
  transform: rotate(18deg) scale(0.62);
}

.bubble-field {
  position: relative;
  z-index: 2;
  min-height: 765px;
  margin-top: 20px;
}

.place-bubble {
  position: absolute;
  width: 202px;
  height: 202px;
  padding: 0;
  border: 0;
  color: inherit;
  background: transparent;
  cursor: pointer;
}

.water-ring {
  position: absolute;
  inset: -22px;
  border-radius: 50%;
  opacity: 0.82;
  background: conic-gradient(
    from 16deg,
    rgba(84, 130, 153, 0.28),
    transparent 10%,
    rgba(84, 130, 153, 0.18) 16%,
    transparent 25%,
    rgba(210, 177, 112, 0.22) 32%,
    transparent 43%,
    rgba(84, 130, 153, 0.24) 52%,
    transparent 70%,
    rgba(84, 130, 153, 0.18) 84%,
    transparent
  );
  mask: radial-gradient(circle, transparent 60%, #000 62%);
}

.bubble-photo {
  position: absolute;
  inset: 0;
  overflow: hidden;
  border-radius: 50%;
  background-position: center;
  background-size: cover;
  box-shadow:
    inset 18px 22px 28px rgba(255, 255, 255, 0.86),
    inset -20px -24px 36px rgba(71, 122, 150, 0.22),
    0 18px 38px rgba(80, 100, 104, 0.18);
}

.bubble-photo::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background:
    radial-gradient(circle at 28% 18%, rgba(255, 255, 255, 0.86), transparent 20%),
    linear-gradient(180deg, rgba(240, 249, 252, 0.36), rgba(255, 248, 232, 0.1));
}

.bubble-glass {
  position: absolute;
  inset: 2px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.72);
  box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.42);
}

.bubble-content {
  position: relative;
  z-index: 2;
  display: grid;
  align-content: center;
  height: 100%;
  padding: 38px 26px 24px;
  text-align: center;
}

.bubble-content h2 {
  margin: 0 0 8px;
  color: #123f58;
  font-family: Georgia, "Songti SC", serif;
  font-size: 21px;
  line-height: 1.3;
}

.bubble-content p {
  margin: 0;
  color: #244b61;
  font-size: 13px;
  line-height: 1.55;
}

.bubble-tags {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 13px;
}

.bubble-tags span {
  max-width: 72px;
  padding: 4px 8px;
  overflow: hidden;
  border-radius: 999px;
  color: #244b61;
  text-overflow: ellipsis;
  white-space: nowrap;
  background: rgba(255, 250, 241, 0.72);
  font-size: 11px;
  box-shadow: 0 4px 12px rgba(81, 75, 62, 0.08);
}

.bubble-0 {
  right: 2px;
  top: 2px;
}

.bubble-1 {
  left: 0;
  top: 174px;
}

.bubble-2 {
  right: 18px;
  top: 352px;
}

.bubble-3 {
  left: 8px;
  top: 528px;
}

.bubble-4 {
  right: 0;
  top: 628px;
  width: 178px;
  height: 178px;
}

.bubble-4 .bubble-content h2 {
  font-size: 20px;
}

.empty-year {
  position: relative;
  z-index: 2;
  min-height: 560px;
  display: grid;
  place-content: center;
  text-align: center;
}

.empty-year h2 {
  margin: 0 0 8px;
  font-size: 22px;
}

.empty-year p {
  max-width: 260px;
  margin: 0 auto;
  color: #687b83;
  line-height: 1.7;
}

.travel-data-card {
  position: relative;
  z-index: 3;
  padding: 20px 16px 18px;
  border: 1px solid rgba(202, 180, 150, 0.44);
  border-radius: 24px;
  background: rgba(255, 252, 247, 0.88);
  box-shadow: 0 18px 42px rgba(86, 64, 41, 0.13);
}

.data-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 18px;
}

.data-title span {
  width: 50px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #d2ad78);
}

.data-title span:last-child {
  background: linear-gradient(90deg, #d2ad78, transparent);
}

.data-title h2 {
  margin: 0;
  color: #123f58;
  font-family: Georgia, "Songti SC", serif;
  font-size: 18px;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.data-item {
  min-width: 0;
  padding: 14px 6px;
  border-radius: 11px;
  color: #123f58;
  text-align: center;
  background: rgba(247, 244, 239, 0.9);
}

.data-item .van-icon {
  color: #918674;
  font-size: 22px;
}

.data-item strong {
  display: block;
  margin-top: 6px;
  font-family: Georgia, serif;
  font-size: 19px;
}

.data-item p {
  margin: 8px 0 0;
  color: #8a8f8e;
  font-size: 11px;
}

.diary-button {
  width: 240px;
  margin: 18px auto 0;
  border: 0;
  color: #fffaf1;
  background: #124b66;
  box-shadow: 0 10px 22px rgba(18, 75, 102, 0.24);
}

.no-export.is-exporting {
  display: none;
}

@media (max-width: 390px) {
  .year-poster {
    padding-inline: 18px;
  }

  .hero-copy {
    margin-left: 60px;
  }

  .place-bubble {
    width: 184px;
    height: 184px;
  }

  .bubble-4 {
    width: 164px;
    height: 164px;
  }

  .bubble-content {
    padding-inline: 22px;
  }

  .bubble-content h2 {
    font-size: 19px;
  }

  .data-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
