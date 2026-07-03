<template>
  <article class="hand-account-shell">
    <section v-if="posterUrl" class="ai-poster-card">
      <img :src="assetUrl(posterUrl)" alt="AI 生成的旅行日志图片" />
      <div class="poster-toolbar">
        <van-button round icon="down" @click="downloadPoster">保存图片</van-button>
        <van-button round icon="replay" :loading="generating" @click="generatePoster">重新生成</van-button>
        <van-button round icon="revoke" @click="backToTemplate">返回模板</van-button>
      </div>
    </section>

    <section v-else ref="pageRef" class="journal-poster" :class="[styleClass, layoutClass]">
      <div class="wash wash-left"></div>
      <div class="wash wash-right"></div>

      <header class="poster-header">
        <p class="poster-title">旅行日志</p>
        <div class="title-divider"><span></span><i></i><span></span></div>
      </header>

      <section class="place-block">
        <p class="date-line">{{ formattedDate }}</p>
        <div class="place-line">
          <van-icon name="location" />
          <h1>{{ record.place }}</h1>
        </div>
        <div class="stamp-card">
          <span>{{ selectedStyle }}</span>
          <strong>{{ cityText }}</strong>
        </div>
      </section>

      <section class="paper-card">
        <div class="quote-mark">“</div>
        <p class="lead-text">{{ leadText }}</p>

        <div v-if="photos.length" class="photo-board" :class="{ single: photos.length === 1 }">
          <figure v-for="(photo, index) in featuredPhotos" :key="photo + index" class="polaroid" :class="`tilt-${index % 2}`">
            <img :src="assetUrl(photo)" alt="旅行照片" />
          </figure>
        </div>
        <div v-else class="empty-photo">
          <van-icon name="photograph" />
          <span>上传照片后会贴在这里</span>
        </div>

        <p class="body-text">{{ bodyText }}</p>

        <div v-if="extraPhotos.length" class="round-photo-row">
          <figure v-for="(photo, index) in extraPhotos" :key="photo + index" class="round-photo">
            <img :src="assetUrl(photo)" alt="旅行照片" />
          </figure>
        </div>

        <div class="note-row">
          <div class="memo-note">
            <span>{{ record.mood || '今日心情' }}</span>
            <p>{{ record.quote || record.share_text || '把这一刻认真收好。' }}</p>
          </div>
          <div class="heart-line">♡</div>
        </div>
      </section>

    </section>

    <section class="style-panel no-export">
      <div class="panel-head">
        <div>
          <h2>选择喜欢的风格</h2>
          <p>{{ posterUrl ? '本次 AI 图片已生成，可按当前风格重新生成' : '点击生成后展示 AI 图片日志' }}</p>
        </div>
        <span>{{ selectedStyle }}</span>
      </div>
      <div class="style-grid">
        <button
          v-for="style in styles"
          :key="style.name"
          class="style-chip"
          :class="{ active: selectedStyle === style.name }"
          type="button"
          @click="selectStyle(style.name)"
        >
          <van-icon :name="style.icon" />
          <span>{{ style.name }}</span>
        </button>
      </div>
      <p v-if="posterJobMessage" class="poster-job-status">{{ posterJobMessage }}</p>
      <div class="action-row">
        <van-button round icon="edit" class="edit-btn" @click="router.push('/chat-generate')">继续创作</van-button>
        <van-button round icon="photograph" type="primary" class="save-btn" :loading="generating" @click="generatePoster">
          {{ posterUrl ? '按当前风格重生成' : 'AI 生成图片日志' }}
        </van-button>
      </div>
    </section>

    <div class="export-bar">
      <van-button block type="primary" class="primary-btn" :loading="exporting" @click="canUsePoster ? downloadPoster() : exportImage()">
        {{ canUsePoster ? '保存 AI 图片日志' : '导出当前手账长图' }}
      </van-button>
    </div>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue'
import { closeToast, showLoadingToast, showToast } from 'vant'
import { useRouter } from 'vue-router'
import html2canvas from 'html2canvas'
import { getTravelPosterJob, startTravelPosterJob } from '../services/api'

const props = defineProps({ record: { type: Object, required: true } })
const router = useRouter()
const pageRef = ref(null)
const exporting = ref(false)
const generating = ref(false)
const posterUrl = ref('')
const selectedStyle = ref(props.record.style || '手账风')
const generatedStyle = ref('')
const posterJobMessage = ref('')
const canUsePoster = computed(() => Boolean(posterUrl.value))
const layoutClass = computed(() => {
  const explicit = props.record.hand_account_layout?.template
  if (explicit) return `layout-${explicit}`
  const seed = [
    props.record.id,
    props.record.place,
    props.record.travel_date,
    props.record.title,
    props.record.memory,
    props.record.content,
    (props.record.image_urls || []).length
  ].filter(Boolean).join('|')
  const variants = ['lead-first', 'photo-first', 'essay-first', 'gallery']
  return `layout-${variants[stableHash(seed) % variants.length]}`
})
const styleClass = computed(() => {
  const map = {
    '手账风': 'style-handbook',
    '小红书风': 'style-redbook',
    '清新风': 'style-fresh',
    '胶片风': 'style-film',
    '文艺风': 'style-literary'
  }
  return map[selectedStyle.value] || 'style-handbook'
})

function stableHash(value) {
  return Array.from(String(value || 'travel')).reduce((sum, char) => {
    return (sum * 31 + char.charCodeAt(0)) >>> 0
  }, 7)
}

const styles = [
  { name: '手账风', icon: 'notes-o' },
  { name: '小红书风', icon: 'flower-o' },
  { name: '清新风', icon: 'leaf-o' },
  { name: '胶片风', icon: 'photograph' },
  { name: '文艺风', icon: 'gem-o' }
]

const layout = computed(() => props.record.hand_account_layout || {})
const sections = computed(() => props.record.section_blocks?.length ? props.record.section_blocks : layout.value.section_blocks || [])
const photos = computed(() => props.record.image_urls || [])
const featuredPhotos = computed(() => photos.value.slice(0, 2))
const extraPhotos = computed(() => photos.value.slice(2, 4))
const formattedDate = computed(() => String(props.record.travel_date || '').replaceAll('-', ' / '))
const cityText = computed(() => String(props.record.place || 'TRAVEL').split(/[·\s,，、-]/)[0].slice(0, 12).toUpperCase())
const leadText = computed(() => {
  const firstSection = sections.value.find((item) => item?.text)?.text
  return firstSection || props.record.location_desc || props.record.memory || props.record.content
})
const bodyText = computed(() => {
  const content = props.record.content || props.record.share_text || ''
  const paragraphs = content.split(/\n+/).filter(Boolean)
  return paragraphs.slice(0, 2).join('\n')
})

function assetUrl(url) {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('data:')) return url
  if (url.startsWith('/uploads')) return url
  return `/uploads/${url.replace(/^\/+/, '')}`
}

async function generatePoster() {
  if (!photos.value.length) {
    showToast({ message: '这篇日志没有上传图片，无法生成 AI 图片日志', duration: 3500 })
    return
  }
  await generatePosterWithStyle(selectedStyle.value)
}

function selectStyle(styleName) {
  if (generating.value) return
  selectedStyle.value = styleName
}

function sleep(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}

async function waitPosterJob(jobId) {
  const maxAttempts = 72
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const { data } = await getTravelPosterJob(jobId)
    if (data.status === 'succeeded' && data.image_url) return data
    if (data.status === 'failed') {
      throw new Error(data.error || 'AI 图片生成失败')
    }
    const elapsed = attempt < 6 ? (attempt + 1) * 3 : 18 + (attempt - 5) * 5
    posterJobMessage.value = `AI 图片日志生成中，已等待约 ${elapsed} 秒，请停留在当前页面。`
    await sleep(attempt < 6 ? 3000 : 5000)
  }
  throw new Error('AI 图片还在生成中，请稍后重新打开这篇日志查看')
}

async function generatePosterWithStyle(styleName) {
  generating.value = true
  posterJobMessage.value = '正在创建 AI 图片生成任务...'
  showLoadingToast({
    message: 'AI 图片日志生成中，可能需要 1-3 分钟...',
    duration: 0,
    forbidClick: false
  })
  let successMessage = ''
  try {
    const { data } = await startTravelPosterJob(props.record.id, styleName)
    posterJobMessage.value = '任务已创建，正在等待 vivo 图片模型返回结果...'
    const result = await waitPosterJob(data.job_id)
    posterUrl.value = result.image_url
    generatedStyle.value = styleName
    posterJobMessage.value = ''
    successMessage = `${styleName}图片日志已生成`
  } catch (error) {
    posterJobMessage.value = error?.response?.data?.detail || error?.message || 'AI 图片生成失败，请检查模型权限'
  } finally {
    closeToast()
    generating.value = false
    if (successMessage) showToast(successMessage)
    else if (posterJobMessage.value) showToast({ message: posterJobMessage.value, duration: 4500 })
  }
}

function backToTemplate() {
  posterUrl.value = ''
  generatedStyle.value = ''
}

function downloadPoster() {
  if (!posterUrl.value) return
  const link = document.createElement('a')
  link.download = `${props.record.title || '旅行日志'}-${selectedStyle.value}.png`
  link.href = assetUrl(posterUrl.value)
  link.click()
}

async function exportImage() {
  if (!pageRef.value) return
  exporting.value = true
  const hidden = pageRef.value.querySelectorAll('.no-export')
  try {
    hidden.forEach((item) => item.classList.add('is-exporting'))
    const canvas = await html2canvas(pageRef.value, {
      backgroundColor: '#f8f1e7',
      scale: 2,
      useCORS: true,
      allowTaint: true,
      scrollY: -window.scrollY
    })
    const link = document.createElement('a')
    link.download = `${props.record.title || '旅行手账'}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    showToast('手账长图已导出')
  } catch (error) {
    showToast('导出失败，请稍后重试')
  } finally {
    hidden.forEach((item) => item.classList.remove('is-exporting'))
    exporting.value = false
  }
}
</script>

<style scoped>
.hand-account-shell {
  padding-bottom: 18px;
}

.ai-poster-card {
  position: relative;
  z-index: 2;
  overflow: hidden;
  margin-bottom: 14px;
  border-radius: 18px;
  background: rgba(255, 250, 241, 0.9);
  box-shadow: var(--shadow-card);
}

.ai-poster-card img {
  display: block;
  width: 100%;
  height: auto;
  max-height: none;
  object-fit: contain;
}

.poster-toolbar {
  display: flex;
  gap: 10px;
  padding: 12px;
}

.poster-toolbar .van-button {
  flex: 1;
}

.journal-poster {
  position: relative;
  overflow: hidden;
  min-height: 860px;
  padding: 34px 28px 24px;
  border-radius: 24px;
  color: #152f3f;
  background:
    radial-gradient(circle at 20% 0%, rgba(210, 178, 125, 0.12), transparent 22%),
    radial-gradient(circle at 84% 12%, rgba(135, 164, 165, 0.19), transparent 20%),
    repeating-linear-gradient(0deg, rgba(120, 102, 78, 0.035), rgba(120, 102, 78, 0.035) 1px, transparent 1px, transparent 22px),
    #fbf5ea;
  box-shadow: 0 18px 42px rgba(77, 59, 39, 0.14);
}

.journal-poster::before,
.journal-poster::after {
  content: "";
  position: absolute;
  pointer-events: none;
  opacity: 0.32;
}

.journal-poster::before {
  left: 24px;
  top: 430px;
  width: 62px;
  height: 62px;
  background:
    linear-gradient(45deg, transparent 46%, #d9b486 48%, transparent 52%),
    linear-gradient(-45deg, transparent 46%, #d9b486 48%, transparent 52%);
}

.journal-poster::after {
  right: 18px;
  bottom: 210px;
  width: 88px;
  height: 58px;
  border-radius: 50%;
  background: rgba(132, 164, 156, 0.16);
}

.wash {
  position: absolute;
  pointer-events: none;
  border-radius: 50%;
  filter: blur(10px);
}

.wash-left {
  left: -34px;
  top: 18px;
  width: 150px;
  height: 70px;
  background: rgba(141, 166, 173, 0.16);
}

.wash-right {
  right: -30px;
  top: 34px;
  width: 158px;
  height: 82px;
  background: rgba(141, 166, 173, 0.18);
}

.poster-header {
  position: relative;
  z-index: 1;
  text-align: center;
}

.poster-title {
  margin: 0;
  color: #123f58;
  font-family: Georgia, "Songti SC", serif;
  font-size: 31px;
  font-weight: 800;
  letter-spacing: 0;
}

.title-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 12px;
}

.title-divider span {
  width: 34px;
  height: 1px;
  background: #d2ad78;
}

.title-divider i {
  width: 8px;
  height: 8px;
  background: #d2ad78;
  transform: rotate(45deg);
}

.place-block {
  position: relative;
  z-index: 1;
  margin-top: 26px;
}

.date-line {
  margin: 0 0 12px 52px;
  color: #28323a;
  font-size: 15px;
}

.place-line {
  display: flex;
  align-items: center;
  gap: 14px;
}

.place-line .van-icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  color: #fff8ec;
  background: #654f39;
  font-size: 21px;
}

.place-line h1 {
  margin: 0;
  max-width: calc(100% - 114px);
  color: #123f58;
  font-family: Georgia, "Songti SC", serif;
  font-size: 30px;
  line-height: 1.25;
}

.stamp-card {
  position: absolute;
  right: 0;
  top: 2px;
  display: grid;
  place-items: center;
  width: 96px;
  height: 78px;
  border: 1px solid rgba(194, 138, 86, 0.55);
  border-radius: 26px;
  color: #b4744d;
  transform: rotate(-7deg);
}

.stamp-card span {
  font-size: 10px;
}

.stamp-card strong {
  font-size: 13px;
  letter-spacing: 0;
}

.paper-card {
  position: relative;
  z-index: 1;
  margin-top: 18px;
  padding: 24px 18px 20px;
  border: 1px solid rgba(224, 204, 177, 0.84);
  border-radius: 8px;
  background:
    linear-gradient(rgba(255, 252, 245, 0.78), rgba(255, 252, 245, 0.86)),
    repeating-linear-gradient(90deg, rgba(200, 180, 150, 0.11), rgba(200, 180, 150, 0.11) 1px, transparent 1px, transparent 18px),
    repeating-linear-gradient(0deg, rgba(200, 180, 150, 0.10), rgba(200, 180, 150, 0.10) 1px, transparent 1px, transparent 18px);
  box-shadow: 0 10px 26px rgba(100, 75, 45, 0.08);
}

.quote-mark {
  position: absolute;
  left: 18px;
  top: 8px;
  color: rgba(200, 160, 105, 0.68);
  font-family: Georgia, serif;
  font-size: 52px;
  line-height: 1;
}

.lead-text,
.body-text {
  margin: 0;
  color: #232b31;
  font-size: 16px;
  line-height: 1.95;
  white-space: pre-line;
}

.lead-text {
  padding-left: 38px;
}

.photo-board {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin: 24px 0 22px;
}

.photo-board.single {
  grid-template-columns: minmax(0, 1fr);
}

.polaroid {
  position: relative;
  margin: 0;
  padding: 8px;
  background: #fffdf8;
  box-shadow: 0 10px 24px rgba(83, 62, 38, 0.16);
}

.polaroid::before {
  content: "";
  position: absolute;
  left: -10px;
  right: -10px;
  top: -8px;
  height: 18px;
  background: rgba(215, 180, 128, 0.32);
  transform: rotate(-5deg);
}

.tilt-0 {
  transform: rotate(-3deg);
}

.tilt-1 {
  transform: rotate(4deg);
}

.polaroid img {
  display: block;
  width: 100%;
  aspect-ratio: 1 / 0.82;
  object-fit: cover;
}

.empty-photo {
  display: grid;
  place-items: center;
  gap: 8px;
  min-height: 150px;
  margin: 22px 0;
  border: 1px dashed rgba(171, 131, 87, 0.42);
  border-radius: 8px;
  color: #5d5147;
  background: rgba(255, 250, 241, 0.58);
}

.round-photo-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 20px;
}

.round-photo {
  flex: 1;
  margin: 0;
  text-align: center;
}

.round-photo img {
  width: 118px;
  max-width: 100%;
  aspect-ratio: 1;
  padding: 5px;
  border-radius: 50%;
  object-fit: cover;
  background: #fffaf1;
  box-shadow: 0 6px 16px rgba(77, 55, 34, 0.14);
}

.note-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-top: 20px;
}

.memo-note {
  max-width: 180px;
  padding: 14px 16px;
  color: #2f3336;
  background: rgba(244, 239, 214, 0.86);
  border-radius: 2px 14px 6px 12px;
  transform: rotate(-2deg);
}

.memo-note::before {
  content: "";
  display: block;
  width: 42px;
  height: 8px;
  margin: -18px auto 10px;
  background: rgba(94, 153, 145, 0.42);
}

.memo-note span {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  text-align: center;
}

.memo-note p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
}

.heart-line {
  color: #d48a67;
  font-size: 52px;
  line-height: 1;
}

.style-panel {
  position: relative;
  z-index: 2;
  margin-top: 24px;
  padding: 18px 16px;
  border-radius: 20px;
  background: rgba(255, 252, 247, 0.92);
  box-shadow: 0 14px 34px rgba(85, 62, 39, 0.12);
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.panel-head h2 {
  margin: 0;
  color: #153f58;
  font-size: 17px;
}

.panel-head p,
.panel-head span {
  margin: 4px 0 0;
  color: #6f6257;
  font-size: 12px;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.style-chip {
  display: grid;
  justify-items: center;
  gap: 6px;
  min-width: 0;
  min-height: 78px;
  padding: 10px 4px 8px;
  border: 1px solid rgba(87, 75, 63, 0.12);
  border-radius: 8px;
  color: #163f57;
  background: rgba(250, 246, 239, 0.86);
  font: inherit;
}

.style-chip.active {
  border-color: #164c68;
  box-shadow: inset 0 0 0 1px #164c68;
}

.style-chip .van-icon {
  font-size: 26px;
}

.style-chip span {
  font-size: 12px;
}


.poster-job-status {
  margin: 12px 0 0;
  color: #7a6b5f;
  font-size: 12px;
  line-height: 1.6;
}

.action-row {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 14px;
  margin-top: 18px;
}

.edit-btn {
  color: #2d3134;
  border-color: rgba(210, 174, 123, 0.36);
  background: #fff5e8;
}

.save-btn {
  border: 0;
  background: #124b66;
}

.export-bar {
  margin-top: 14px;
}

.no-export.is-exporting {
  display: none;
}

.layout-lead-first .paper-card,
.layout-photo-first .paper-card,
.layout-essay-first .paper-card,
.layout-note-first .paper-card,
.layout-gallery .paper-card {
  display: flex;
  flex-direction: column;
}

.layout-lead-first .lead-text { order: 1; }
.layout-lead-first .photo-board,
.layout-lead-first .empty-photo { order: 2; }
.layout-lead-first .body-text { order: 3; }
.layout-lead-first .round-photo-row { order: 4; }
.layout-lead-first .note-row { order: 5; }

.layout-photo-first .quote-mark {
  right: 18px;
  left: auto;
  top: 16px;
}

.layout-photo-first .photo-board,
.layout-photo-first .empty-photo {
  order: 1;
  margin-top: 0;
}

.layout-photo-first .lead-text {
  order: 2;
  padding-left: 0;
  margin-top: 8px;
  font-size: 18px;
  font-weight: 700;
}

.layout-photo-first .body-text { order: 3; }
.layout-photo-first .round-photo-row { order: 4; }
.layout-photo-first .note-row { order: 5; }
.layout-photo-first .polaroid:first-child img { aspect-ratio: 1 / 0.72; }

.layout-essay-first .lead-text {
  order: 1;
  padding-left: 34px;
  font-family: Georgia, "Songti SC", serif;
  font-size: 19px;
}

.layout-essay-first .body-text {
  order: 2;
  margin-top: 18px;
}

.layout-essay-first .photo-board,
.layout-essay-first .empty-photo {
  order: 3;
  width: 82%;
  align-self: flex-end;
}

.layout-essay-first .round-photo-row { order: 4; }
.layout-essay-first .note-row { order: 5; }
.layout-essay-first .photo-board:not(.single) { grid-template-columns: 1fr; }
.layout-essay-first .polaroid { transform: rotate(1deg); }

.layout-note-first .quote-mark { display: none; }
.layout-note-first .note-row {
  order: 1;
  align-items: center;
  margin: 0 0 22px;
}

.layout-note-first .memo-note {
  max-width: none;
  width: 72%;
}

.layout-note-first .heart-line {
  font-size: 38px;
}

.layout-note-first .lead-text {
  order: 2;
  padding-left: 0;
}

.layout-note-first .photo-board,
.layout-note-first .empty-photo { order: 3; }
.layout-note-first .body-text { order: 4; }
.layout-note-first .round-photo-row { order: 5; }

.layout-gallery .quote-mark { display: none; }
.layout-gallery .photo-board,
.layout-gallery .empty-photo {
  order: 1;
  margin-top: 0;
}

.layout-gallery .photo-board:not(.single) {
  grid-template-columns: 1.18fr 0.82fr;
  align-items: stretch;
}

.layout-gallery .polaroid {
  padding: 6px;
  transform: none;
}

.layout-gallery .polaroid:first-child {
  grid-row: span 2;
}

.layout-gallery .polaroid:first-child img {
  height: 100%;
  aspect-ratio: 1 / 1.18;
}

.layout-gallery .lead-text {
  order: 2;
  padding-left: 0;
  margin-top: 10px;
}

.layout-gallery .round-photo-row {
  order: 3;
  justify-content: center;
}

.layout-gallery .body-text { order: 4; }
.layout-gallery .note-row { order: 5; }
.style-redbook {
  min-height: 760px;
  padding: 24px 18px;
  color: #26272b;
  background:
    linear-gradient(135deg, rgba(255, 86, 106, 0.10), transparent 32%),
    linear-gradient(315deg, rgba(255, 200, 72, 0.16), transparent 34%),
    #fffaf8;
}

.style-redbook .wash,
.style-redbook .title-divider,
.style-redbook::before,
.style-redbook::after {
  display: none;
}

.style-redbook .poster-header {
  text-align: left;
}

.style-redbook .poster-title {
  color: #241f23;
  font-family: Arial, "Microsoft YaHei", sans-serif;
  font-size: 26px;
  font-weight: 900;
}

.style-redbook .place-block {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  margin-top: 14px;
}

.style-redbook .date-line {
  grid-column: 1 / -1;
  margin: 0;
  color: #e94f64;
  font-weight: 700;
}

.style-redbook .place-line h1 {
  color: #231f20;
  font-family: Arial, "Microsoft YaHei", sans-serif;
  font-size: 32px;
  font-weight: 900;
}

.style-redbook .place-line .van-icon {
  background: #ff5b6d;
}

.style-redbook .stamp-card {
  position: static;
  width: 82px;
  height: 54px;
  border: 0;
  border-radius: 18px;
  color: #fff;
  background: #ff5b6d;
  transform: rotate(0deg);
}

.style-redbook .paper-card {
  margin-top: 18px;
  padding: 16px;
  border: 0;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 12px 26px rgba(233, 79, 100, 0.16);
}

.style-redbook .quote-mark,
.style-redbook .heart-line {
  display: none;
}

.style-redbook .lead-text {
  padding-left: 0;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.65;
}

.style-redbook .photo-board {
  gap: 8px;
  margin: 16px 0;
}

.style-redbook .polaroid {
  overflow: hidden;
  padding: 0;
  border-radius: 16px;
  box-shadow: none;
  transform: none;
}

.style-redbook .polaroid::before {
  display: none;
}

.style-redbook .memo-note {
  max-width: none;
  border-radius: 16px;
  color: #5d2931;
  background: #fff0f2;
  transform: none;
}

.style-fresh {
  min-height: 760px;
  color: #1f4652;
  background:
    radial-gradient(circle at 12% 18%, rgba(158, 221, 204, 0.32), transparent 28%),
    radial-gradient(circle at 86% 78%, rgba(255, 231, 148, 0.26), transparent 28%),
    #fbfffc;
}

.style-fresh .poster-title,
.style-fresh .place-line h1 {
  color: #245d69;
  font-family: Arial, "Microsoft YaHei", sans-serif;
  font-weight: 600;
}

.style-fresh .title-divider span,
.style-fresh .title-divider i {
  background: #8fd5c5;
}

.style-fresh .place-line .van-icon {
  background: #72b9ad;
}

.style-fresh .stamp-card {
  border-color: rgba(114, 185, 173, 0.45);
  color: #378173;
  border-radius: 999px;
  transform: rotate(4deg);
}

.style-fresh .paper-card {
  border: 0;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 14px 34px rgba(76, 139, 129, 0.13);
}

.style-fresh .quote-mark {
  color: rgba(143, 213, 197, 0.7);
}

.style-fresh .photo-board {
  grid-template-columns: 1fr;
}

.style-fresh .polaroid {
  overflow: hidden;
  padding: 0;
  border-radius: 26px 26px 8px 26px;
  box-shadow: 0 12px 24px rgba(84, 145, 138, 0.14);
  transform: none;
}

.style-fresh .polaroid::before {
  display: none;
}

.style-fresh .polaroid img {
  aspect-ratio: 1 / 0.7;
}

.style-fresh .memo-note {
  border-radius: 18px;
  background: rgba(226, 247, 239, 0.92);
  transform: rotate(1deg);
}

.style-film {
  min-height: 760px;
  color: #f7e8cf;
  background:
    linear-gradient(90deg, rgba(0, 0, 0, 0.28), transparent 18%, transparent 82%, rgba(0, 0, 0, 0.30)),
    radial-gradient(circle at 26% 20%, rgba(214, 127, 54, 0.28), transparent 34%),
    #2a241f;
}

.style-film .wash,
.style-film .title-divider,
.style-film::before,
.style-film::after {
  display: none;
}

.style-film .poster-title,
.style-film .place-line h1 {
  color: #ffe0ae;
  font-family: Georgia, serif;
}

.style-film .date-line,
.style-film .lead-text,
.style-film .body-text {
  color: #f3dec2;
}

.style-film .place-line .van-icon {
  color: #2a241f;
  background: #f2c276;
}

.style-film .stamp-card {
  border-color: rgba(242, 194, 118, 0.72);
  color: #f2c276;
  border-radius: 4px;
  transform: rotate(0deg);
}

.style-film .paper-card {
  border: 1px solid rgba(242, 194, 118, 0.32);
  border-radius: 6px;
  background: rgba(24, 20, 18, 0.72);
  box-shadow: inset 0 0 0 10px rgba(0, 0, 0, 0.18);
}

.style-film .photo-board {
  grid-template-columns: 1fr;
  gap: 12px;
}

.style-film .polaroid {
  padding: 12px 12px 26px;
  background: #161412;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.34);
  transform: none;
}

.style-film .polaroid::before {
  left: 0;
  right: 0;
  top: auto;
  bottom: 6px;
  height: 10px;
  background: repeating-linear-gradient(90deg, #f1d19f 0 8px, transparent 8px 16px);
  transform: none;
}

.style-film .memo-note {
  color: #321f15;
  background: #e0b06d;
  transform: rotate(0deg);
}

.style-film .heart-line {
  color: #f2c276;
}

.style-literary {
  min-height: 760px;
  padding-top: 42px;
  color: #1e252b;
  background:
    linear-gradient(90deg, transparent 0 78%, rgba(24, 37, 45, 0.05) 78% 79%, transparent 79%),
    #fffdf8;
}

.style-literary .wash,
.style-literary::before,
.style-literary::after,
.style-literary .place-line .van-icon,
.style-literary .heart-line {
  display: none;
}

.style-literary .poster-header,
.style-literary .place-block {
  text-align: left;
}

.style-literary .poster-title {
  color: #15191d;
  font-family: Georgia, "Songti SC", serif;
  font-size: 20px;
  font-weight: 400;
}

.style-literary .title-divider {
  justify-content: flex-start;
}

.style-literary .title-divider span {
  width: 78px;
  background: #1e252b;
}

.style-literary .title-divider i {
  display: none;
}

.style-literary .date-line {
  margin-left: 0;
  color: #7d6c58;
  font-style: italic;
}

.style-literary .place-line h1 {
  max-width: 100%;
  color: #15191d;
  font-family: Georgia, "Songti SC", serif;
  font-size: 36px;
  font-weight: 400;
}

.style-literary .stamp-card {
  top: -14px;
  width: 76px;
  height: 76px;
  border-radius: 50%;
  color: #1e252b;
  transform: rotate(0deg);
}

.style-literary .paper-card {
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.style-literary .quote-mark {
  display: none;
}

.style-literary .lead-text {
  padding-left: 0;
  color: #20262c;
  font-family: Georgia, "Songti SC", serif;
  font-size: 20px;
  line-height: 1.9;
}

.style-literary .photo-board {
  grid-template-columns: 1fr;
  margin: 22px 0;
}

.style-literary .polaroid {
  padding: 0;
  border: 1px solid rgba(30, 37, 43, 0.14);
  background: transparent;
  box-shadow: none;
  transform: none;
}

.style-literary .polaroid::before {
  display: none;
}

.style-literary .polaroid img {
  aspect-ratio: 1 / 0.76;
}

.style-literary .memo-note {
  max-width: 220px;
  border-left: 2px solid #1e252b;
  border-radius: 0;
  background: transparent;
  transform: none;
}
@media (max-width: 390px) {
  .journal-poster {
    padding-inline: 20px;
  }

  .stamp-card {
    position: relative;
    right: auto;
    top: auto;
    margin: 14px 0 0 auto;
  }

  .place-line h1 {
    max-width: calc(100% - 48px);
  }

  .style-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
