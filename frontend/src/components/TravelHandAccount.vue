<template>
  <article class="hand-account-shell">
    <section v-if="posterUrl" class="ai-poster-card">
      <img :src="assetUrl(posterUrl)" alt="AI 生成的旅行日志图片" />
      <div class="poster-toolbar">
        <van-button round icon="down" @click="downloadPoster">保存图片</van-button>
        <van-button round icon="replay" :loading="generating" @click="generatePoster">重新生成</van-button>
      </div>
    </section>

    <section v-else ref="pageRef" class="journal-poster">
      <div class="wash wash-left"></div>
      <div class="wash wash-right"></div>

      <div class="poster-actions no-export">
        <van-button round icon="arrow-left" @click="router.back()" />
        <van-button round icon="share-o" @click="exportImage" />
      </div>

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
            <figcaption>{{ photoCaption(index) }}</figcaption>
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
            <figcaption>{{ extraCaption(index) }}</figcaption>
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
          <p>{{ posterUrl ? '点击风格会重新调用大模型生成对应图片' : '调用大模型生成一张图片类型旅行日志' }}</p>
        </div>
        <span>{{ posterUrl ? '当前 ' + selectedStyle : 'AI 图片' }}</span>
      </div>
      <div class="style-grid">
        <button
          v-for="style in styles"
          :key="style.name"
          class="style-chip"
          :class="{ active: selectedStyle === style.name }"
          type="button"
          :disabled="generating"
          @click="selectStyle(style.name)"
        >
          <van-icon :name="style.icon" />
          <span>{{ style.name }}</span>
        </button>
      </div>
      <div class="action-row">
        <van-button round icon="edit" class="edit-btn" @click="router.push('/chat-generate')">继续创作</van-button>
        <van-button round icon="photograph" type="primary" class="save-btn" :loading="generating" @click="generatePoster">
          {{ posterUrl ? '按当前风格重生成' : 'AI 生成图片日志' }}
        </van-button>
      </div>
    </section>

    <div class="export-bar">
      <van-button block type="primary" class="primary-btn" :loading="exporting" @click="posterUrl ? downloadPoster() : exportImage()">
        {{ posterUrl ? '保存 AI 图片日志' : '导出当前手账长图' }}
      </van-button>
    </div>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import html2canvas from 'html2canvas'
import { generateTravelPoster } from '../services/api'

const props = defineProps({ record: { type: Object, required: true } })
const router = useRouter()
const pageRef = ref(null)
const exporting = ref(false)
const generating = ref(false)
const posterUrl = ref(props.record.generated_image_url || '')
const selectedStyle = ref(props.record.style || '手账风')
const generatedStyle = ref(props.record.generated_image_url ? selectedStyle.value : '')

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

function photoCaption(index) {
  const fallbacks = [props.record.place, props.record.mood, selectedStyle.value].filter(Boolean)
  return props.record.stickers?.[index] || props.record.mood_tags?.[index] || fallbacks[index] || `照片 ${index + 1}`
}

function extraCaption(index) {
  return props.record.stickers?.[index + 2] || props.record.mood_tags?.[index + 2] || '旅途片刻'
}

async function generatePoster() {
  await generatePosterWithStyle(selectedStyle.value)
}

async function selectStyle(styleName) {
  if (generating.value) return
  selectedStyle.value = styleName
  await generatePosterWithStyle(styleName)
}

async function generatePosterWithStyle(styleName) {
  generating.value = true
  try {
    const { data } = await generateTravelPoster(props.record.id, styleName)
    posterUrl.value = data.image_url
    generatedStyle.value = styleName
    showToast(`${styleName}图片日志已生成`)
  } catch (error) {
    showToast(error?.response?.data?.detail || 'AI 图片生成失败，请检查模型权限')
  } finally {
    generating.value = false
  }
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
  padding: 72px 28px 24px;
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

.poster-actions {
  position: absolute;
  inset: 24px 22px auto;
  z-index: 4;
  display: flex;
  justify-content: space-between;
}

.poster-actions :deep(.van-button) {
  width: 48px;
  height: 48px;
  color: #17455e;
  background: rgba(250, 240, 224, 0.92);
  border: 0;
  box-shadow: 0 8px 20px rgba(88, 66, 42, 0.18);
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
  padding: 8px 8px 28px;
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

.polaroid figcaption {
  position: absolute;
  left: 8px;
  right: 8px;
  bottom: 6px;
  color: #8b3528;
  font-family: "KaiTi", "STKaiti", serif;
  font-size: 16px;
  text-align: center;
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

.round-photo figcaption {
  margin-top: 6px;
  color: #873728;
  font-family: "KaiTi", "STKaiti", serif;
  font-size: 14px;
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
