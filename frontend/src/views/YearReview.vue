<template>
  <main class="year-review-page">
    <section ref="posterRef" class="year-poster">
      <div class="soft-leaf leaf-left"></div>
      <div class="soft-leaf leaf-right"></div>
      <div class="bird bird-a"></div>
      <div class="bird bird-b"></div>
      <div class="bird bird-c"></div>

      <div class="top-actions no-export">
        <van-button round icon="arrow-left" @click="handleBack" />
        <van-button round icon="share-o" @click="exportImage" />
      </div>

      <header class="hero-copy">
        <h1>这一年，你的足迹</h1>
        <p>{{ reviewYear }} · Year in Review</p>
        <span>{{ heroSubtitle }}</span>
        <i></i>
      </header>

      <section v-if="provinceGroups.length" class="bubble-field" :class="{ 'is-detail': selectedProvince || selectedCity }">
        <div class="bubble-canvas" :style="bubbleCanvasStyle">
          <template v-if="!selectedProvince">
            <article
              v-for="(group, index) in provinceGroups"
              :key="group.province"
              class="place-bubble city-bubble"
              :class="`bubble-${index}`"
              @click="openProvince(group)"
            >
              <div class="water-ring"></div>
              <div class="bubble-photo" :style="groupBubbleStyle(group, index)"></div>
              <div class="bubble-glass"></div>
              <div class="bubble-content">
                <h2>{{ group.province }}</h2>
                <p>{{ provinceSummary(group) }}</p>
                <div class="bubble-tags">
                  <span>{{ group.cities.length }} 城</span>
                  <span>{{ group.records.length }} 篇</span>
                </div>
              </div>
            </article>
          </template>

          <template v-else-if="!selectedCity">
            <section class="city-detail-panel">
              <button class="city-back" type="button" @click="selectedProvince = null">
                <van-icon name="arrow-left" />
                省份足迹
              </button>
              <div>
                <p>{{ selectedProvince.records.length }} 篇旅行日志</p>
                <h2>{{ selectedProvince.province }}</h2>
              </div>
            </section>

            <article
              v-for="(group, index) in selectedProvince.cities"
              :key="group.city"
              class="place-bubble city-bubble"
              :class="`detail-bubble-${index}`"
              @click="openCity(group)"
            >
              <div class="water-ring"></div>
              <div class="bubble-photo" :style="groupBubbleStyle(group, index)"></div>
              <div class="bubble-glass"></div>
              <div class="bubble-content">
                <h2>{{ group.city }}</h2>
                <p>{{ groupSummary(group) }}</p>
                <div class="bubble-tags">
                  <span>{{ group.records.length }} 篇</span>
                  <span v-for="tag in groupTags(group)" :key="tag">#{{ tag }}</span>
                </div>
              </div>
            </article>
          </template>

          <template v-else>
            <section class="city-detail-panel">
              <button class="city-back" type="button" @click="selectedCity = null">
                <van-icon name="arrow-left" />
                城市足迹
              </button>
              <div>
                <p>{{ selectedCity.records.length }} 篇旅行日志</p>
                <h2>{{ selectedCity.city }}</h2>
              </div>
            </section>

            <article
              v-for="(item, index) in selectedCity.records"
              :key="item.id"
              class="place-bubble log-bubble"
              :class="`detail-bubble-${index}`"
              @click="goDetail(item.id)"
            >
              <div class="water-ring"></div>
              <div class="bubble-photo" :style="bubbleStyle(item, index)"></div>
              <div class="bubble-glass"></div>
              <div class="bubble-content">
                <h2>{{ logBubbleTitle(item) }}</h2>
                <p>{{ bubbleSubtitle(item, index) }}</p>
                <div class="bubble-tags">
                  <span v-for="tag in bubbleTags(item, index)" :key="tag">#{{ tag }}</span>
                </div>
              </div>
            </article>
          </template>
        </div>
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
            <p>步行里程</p>
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
const selectedProvince = ref(null)
const selectedCity = ref(null)
const posterRef = ref(null)
const reviewYear = new Date().getFullYear()

const cityProvinceMap = {
  北京: '北京', 上海: '上海', 天津: '天津', 重庆: '重庆',
  杭州: '浙江', 宁波: '浙江', 温州: '浙江', 绍兴: '浙江', 湖州: '浙江', 嘉兴: '浙江', 舟山: '浙江',
  南京: '江苏', 苏州: '江苏', 无锡: '江苏', 扬州: '江苏', 镇江: '江苏', 常州: '江苏',
  昆明: '云南', 大理: '云南', 丽江: '云南', 香格里拉: '云南', 西双版纳: '云南', 腾冲: '云南',
  成都: '四川', 乐山: '四川', 绵阳: '四川', 都江堰: '四川', 九寨沟: '四川',
  广州: '广东', 深圳: '广东', 珠海: '广东', 佛山: '广东', 汕头: '广东',
  兰州: '甘肃', 敦煌: '甘肃', 嘉峪关: '甘肃', 张掖: '甘肃',
  西宁: '青海', 海西: '青海', 玉树: '青海', 果洛: '青海', 青海: '青海'
}

const landmarkRegions = {
  玉龙雪山: { province: '云南', city: '丽江' },
  虎跳峡: { province: '云南', city: '丽江' },
  丽江古城: { province: '云南', city: '丽江' },
  束河古镇: { province: '云南', city: '丽江' },
  曲院风荷: { province: '浙江', city: '杭州' },
  西湖: { province: '浙江', city: '杭州' },
  断桥: { province: '浙江', city: '杭州' },
  灵隐寺: { province: '浙江', city: '杭州' },
  鸣沙山: { province: '甘肃', city: '敦煌' },
  月牙泉: { province: '甘肃', city: '敦煌' },
  莫高窟: { province: '甘肃', city: '敦煌' }
}

const scenicFallbacks = [
  { tags: ['古都韵味', '慢时光'], image: 'linear-gradient(145deg, rgba(205,226,239,.88), rgba(242,228,203,.76)), radial-gradient(circle at 68% 70%, rgba(145,81,45,.52), transparent 28%)' },
  { tags: ['治愈风景', '安静'], image: 'linear-gradient(145deg, rgba(211,231,238,.9), rgba(232,244,238,.7)), radial-gradient(circle at 50% 78%, rgba(53,143,166,.55), transparent 34%)' },
  { tags: ['蓝色海岸', '追风'], image: 'linear-gradient(145deg, rgba(200,225,238,.88), rgba(246,238,216,.72)), radial-gradient(circle at 72% 72%, rgba(93,116,89,.52), transparent 30%)' },
  { tags: ['都市夜景', '记忆'], image: 'linear-gradient(145deg, rgba(210,225,237,.9), rgba(232,219,201,.72)), radial-gradient(circle at 62% 76%, rgba(70,75,118,.58), transparent 30%)' },
  { tags: ['地方美食', '烟火'], image: 'linear-gradient(145deg, rgba(237,225,203,.9), rgba(219,235,229,.76)), radial-gradient(circle at 58% 74%, rgba(197,151,91,.55), transparent 30%)' }
]

const yearRecords = computed(() => {
  const currentYearRecords = records.value.filter((item) => String(item.travel_date || '').startsWith(String(reviewYear)))
  return currentYearRecords.length ? currentYearRecords : records.value
})

const provinceGroups = computed(() => {
  const groups = new Map()
  yearRecords.value.forEach((item) => {
    recordRegions(item).forEach((region) => {
      if (!groups.has(region.province)) {
        groups.set(region.province, { province: region.province, records: [], cityMap: new Map(), cities: [] })
      }
      const provinceGroup = groups.get(region.province)
      addUniqueRecord(provinceGroup.records, item)
      if (!provinceGroup.cityMap.has(region.city)) {
        const cityGroup = { province: region.province, city: region.city, records: [] }
        provinceGroup.cityMap.set(region.city, cityGroup)
        provinceGroup.cities.push(cityGroup)
      }
      addUniqueRecord(provinceGroup.cityMap.get(region.city).records, item)
    })
  })
  return [...groups.values()].map((group) => ({
    ...group,
    cities: group.cities.sort(sortGroups)
  })).sort(sortGroups)
})

const activeBubbleCount = computed(() => {
  if (selectedCity.value) return selectedCity.value.records.length
  if (selectedProvince.value) return selectedProvince.value.cities.length
  return provinceGroups.value.length
})
const cityCount = computed(() => provinceGroups.value.reduce((sum, group) => sum + group.cities.length, 0))
const bubbleCanvasStyle = computed(() => {
  const base = selectedProvince.value || selectedCity.value ? 640 : 765
  const extra = Math.max(0, activeBubbleCount.value - 5) * 170
  return { minHeight: `${base + extra}px` }
})
const heroSubtitle = computed(() => {
  if (selectedCity.value) return `${selectedCity.value.city} 的旅行日志`
  if (selectedProvince.value) return `${selectedProvince.value.province} 的城市足迹`
  return '每一个省份，都是这一年走过的章节。'
})
const photoCount = computed(() => records.value.reduce((sum, item) => sum + (item.image_urls?.length || 0), 0))
const stepCount = computed(() => (records.value.length * 6820 + cityCount.value * 1846).toLocaleString())

function sortGroups(a, b) {
  const latestA = String(a.records[0]?.travel_date || '')
  const latestB = String(b.records[0]?.travel_date || '')
  return latestB.localeCompare(latestA) || b.records.length - a.records.length
}

function addUniqueRecord(list, item) {
  if (!list.some((record) => record.id === item.id)) list.push(item)
}

function openProvince(group) {
  selectedProvince.value = group
  selectedCity.value = null
}

function openCity(group) {
  selectedCity.value = group
}

function handleBack() {
  if (selectedCity.value) {
    selectedCity.value = null
    return
  }
  if (selectedProvince.value) {
    selectedProvince.value = null
    return
  }
  router.back()
}

function goDetail(id) {
  router.push(`/travel/${id}`)
}

function normalizeCityLabel(value = '') {
  return String(value).trim().replace(/(省|市|区|县)$/g, '')
}

function uniqueRegions(values = []) {
  const seen = new Set()
  return values.map((value) => ({
    province: normalizeCityLabel(value.province || ''),
    city: normalizeCityLabel(value.city || value.province || '')
  })).filter((region) => {
    if (!region.province && region.city) region.province = cityProvinceMap[region.city] || region.city
    if (!region.province || !region.city) return false
    const key = `${region.province}/${region.city}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

function recordRegions(item) {
  const explicit = uniqueRegions(item?.place_regions || [])
  if (explicit.length) return explicit

  const text = [item?.place, item?.normalized_place, item?.title, item?.content].filter(Boolean).join(' ')
  const landmarkMatches = Object.entries(landmarkRegions).filter(([name]) => text.includes(name)).map(([, region]) => region)
  if (landmarkMatches.length) return uniqueRegions(landmarkMatches)

  const cities = uniqueCityList(item?.places?.length ? item.places : [item?.city || rawPlaceName(item?.place)])
  return uniqueRegions(cities.map((city) => ({ province: cityProvinceMap[city] || city, city })))
}

function uniqueCityList(values = []) {
  const seen = new Set()
  return values.map((value) => normalizeCityLabel(value)).filter((value) => {
    if (!value || seen.has(value)) return false
    seen.add(value)
    return true
  })
}

function rawPlaceName(place = '') {
  return String(place).split(/[·\s,，、/|-]/).map((part) => part.trim()).filter(Boolean)[0] || ''
}

function logBubbleTitle(item) {
  const city = selectedCity.value?.city || ''
  const raw = item.normalized_place || rawPlaceName(item.place)
  if (raw && city && raw !== city && raw.startsWith(city)) return raw.slice(city.length) || raw
  return raw || item.title || '旅行片刻'
}

function provinceSummary(group) {
  const cities = group.cities.map((item) => item.city)
  if (cities.length > 1) return `${cities.slice(0, 3).join('、')}，都收进这一省的足迹。`
  return group.records[0]?.location_desc || group.records[0]?.share_text || compact(group.records[0]?.content, 22) || '值得回看的省份记忆'
}

function groupSummary(group) {
  const places = [...new Set(group.records.map((item) => logBubbleTitleForGroup(group.city, item)).filter(Boolean))]
  if (places.length > 1) return `${places.slice(0, 3).join('、')}，都收进这一座城市。`
  return group.records[0]?.location_desc || group.records[0]?.share_text || compact(group.records[0]?.content, 22) || '值得回看的城市记忆'
}

function logBubbleTitleForGroup(city, item) {
  const raw = item.normalized_place || rawPlaceName(item.place)
  if (raw && raw !== city && raw.startsWith(city)) return raw.slice(city.length) || raw
  return item.title || raw
}

function groupTags(group) {
  const tags = group.records.flatMap((item) => [...(item.mood_tags || []), ...(item.stickers || [])]).filter(Boolean)
  return [...new Set(tags)].slice(0, 1)
}

function bubbleSubtitle(item, index) {
  return item?.location_desc || item?.share_text || compact(item?.content, 20) || scenicFallbacks[index]?.subtitle || '值得收藏的一段旅程'
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

function groupBubbleStyle(group, index) {
  const withImage = group.records.find((item) => item.image_urls?.length)
  return bubbleStyle(withImage || group.records[0], index)
}

function bubbleStyle(item, index) {
  const uploaded = item?.image_urls?.[0]
  if (uploaded) {
    return { backgroundImage: `linear-gradient(180deg, rgba(225,239,246,.18), rgba(245,239,222,.2)), url("${assetUrl(uploaded)}")` }
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
  height: 100vh;
  max-width: 430px;
  margin: 0 auto;
  overflow: hidden;
  color: #123f58;
  background: #f8f1e7;
}

.year-poster {
  position: relative;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 76px 24px 16px;
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
  flex: 1;
  min-height: 0;
  margin-top: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}

.bubble-canvas {
  position: relative;
}

.bubble-field.is-detail {
  padding-top: 0;
}

.bubble-field.is-detail .bubble-canvas {
  padding-top: 96px;
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
  background: conic-gradient(from 16deg, rgba(84, 130, 153, 0.28), transparent 10%, rgba(84, 130, 153, 0.18) 16%, transparent 25%, rgba(210, 177, 112, 0.22) 32%, transparent 43%, rgba(84, 130, 153, 0.24) 52%, transparent 70%, rgba(84, 130, 153, 0.18) 84%, transparent);
  mask: radial-gradient(circle, transparent 60%, #000 62%);
}

.bubble-photo {
  position: absolute;
  inset: 0;
  overflow: hidden;
  border-radius: 50%;
  background-position: center;
  background-size: cover;
  box-shadow: inset 18px 22px 28px rgba(255, 255, 255, 0.86), inset -20px -24px 36px rgba(71, 122, 150, 0.22), 0 18px 38px rgba(80, 100, 104, 0.18);
}

.bubble-photo::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: radial-gradient(circle at 28% 18%, rgba(255, 255, 255, 0.86), transparent 20%), linear-gradient(180deg, rgba(240, 249, 252, 0.36), rgba(255, 248, 232, 0.1));
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

.city-bubble .bubble-content h2 {
  font-size: 25px;
}

.bubble-content p {
  display: -webkit-box;
  max-height: 62px;
  margin: 0;
  overflow: hidden;
  color: #244b61;
  font-size: 13px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
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

.bubble-0 { right: 2px; top: 2px; }
.bubble-1 { left: 0; top: 174px; }
.bubble-2 { right: 18px; top: 352px; }
.bubble-3 { left: 8px; top: 528px; }
.bubble-4 { right: 0; top: 628px; width: 178px; height: 178px; }
.bubble-4 .bubble-content h2 { font-size: 20px; }
.bubble-5 { left: 6px; top: 798px; width: 176px; height: 176px; }
.bubble-6 { right: 12px; top: 934px; width: 188px; height: 188px; }
.bubble-7 { left: 18px; top: 1096px; width: 170px; height: 170px; }
.bubble-8 { right: 4px; top: 1228px; width: 178px; height: 178px; }
.bubble-9 { left: 2px; top: 1392px; width: 184px; height: 184px; }
.bubble-10 { right: 20px; top: 1538px; width: 170px; height: 170px; }
.bubble-11 { left: 18px; top: 1690px; width: 176px; height: 176px; }

.city-detail-panel {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border: 1px solid rgba(202, 180, 150, 0.42);
  border-radius: 18px;
  background: rgba(255, 252, 247, 0.78);
  box-shadow: 0 12px 30px rgba(86, 64, 41, 0.1);
  backdrop-filter: blur(14px);
}

.city-detail-panel p {
  margin: 0 0 3px;
  color: #8a7c70;
  font-size: 12px;
  text-align: right;
}

.city-detail-panel h2 {
  margin: 0;
  color: #123f58;
  font-family: Georgia, "Songti SC", serif;
  font-size: 24px;
}

.city-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 12px;
  border: 1px solid rgba(18, 75, 102, 0.16);
  border-radius: 999px;
  color: #123f58;
  background: rgba(255, 250, 241, 0.74);
  font-size: 13px;
}

.detail-bubble-0 { left: 4px; top: 116px; }
.detail-bubble-1 { right: 2px; top: 288px; }
.detail-bubble-2 { left: 18px; top: 462px; width: 184px; height: 184px; }
.detail-bubble-3 { right: 10px; top: 610px; width: 174px; height: 174px; }
.detail-bubble-4 { left: 4px; top: 748px; width: 168px; height: 168px; }

.empty-bubbles {
  position: relative;
  z-index: 2;
  min-height: 560px;
  display: grid;
  place-content: center;
  text-align: center;
}

.empty-bubbles h2 { margin: 0 0 8px; font-size: 22px; }
.empty-bubbles p { max-width: 260px; margin: 0 auto; color: #687b83; line-height: 1.7; }

.travel-data-card {
  position: relative;
  z-index: 3;
  flex-shrink: 0;
  margin-top: 12px;
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

.data-title span { width: 50px; height: 1px; background: linear-gradient(90deg, transparent, #d2ad78); }
.data-title span:last-child { background: linear-gradient(90deg, #d2ad78, transparent); }
.data-title h2 { margin: 0; color: #123f58; font-family: Georgia, "Songti SC", serif; font-size: 18px; }

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

.data-item .van-icon { color: #918674; font-size: 22px; }
.data-item strong { display: block; margin-top: 6px; font-family: Georgia, serif; font-size: 19px; }
.data-item p { margin: 8px 0 0; color: #8a8f8e; font-size: 11px; }

.diary-button {
  width: 240px;
  margin: 18px auto 0;
  border: 0;
  color: #fffaf1;
  background: #124b66;
  box-shadow: 0 10px 22px rgba(18, 75, 102, 0.24);
}

.no-export.is-exporting { display: none; }

@media (max-width: 390px) {
  .year-poster { padding-inline: 18px; }
  .hero-copy { margin-left: 60px; }
  .place-bubble { width: 184px; height: 184px; }
  .bubble-4,
  .detail-bubble-2,
  .detail-bubble-3,
  .detail-bubble-4 { width: 164px; height: 164px; }
  .bubble-content { padding-inline: 22px; }
  .bubble-content h2,
  .city-bubble .bubble-content h2 { font-size: 19px; }
  .data-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>