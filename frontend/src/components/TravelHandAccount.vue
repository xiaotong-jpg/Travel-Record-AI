<template>
  <article ref="pageRef" class="hand-page">
    <div class="cover">
      <p class="stamp">{{ record.style || '手账风' }}</p>
      <h1>{{ record.title }}</h1>
      <p>{{ record.place }} · {{ record.travel_date }}</p>
    </div>

    <PhotoFilmStrip :images="record.image_urls" />

    <div class="tag-row">
      <StickerTag v-for="tag in record.mood_tags" :key="tag" :label="tag" />
      <StickerTag v-for="tag in record.stickers" :key="tag" :label="tag" />
    </div>

    <JournalSection title="这一页的风景" :text="record.location_desc" />
    <JournalSection type="journal" title="旅行日志" :text="record.content" />

    <div v-if="sections.length" class="section-stack">
      <JournalSection
        v-for="(section, index) in sections"
        :key="index"
        :type="section.type"
        :title="section.title"
        :text="section.text"
      />
    </div>

    <section v-if="timeline.length" class="soft-card timeline-card">
      <h3>回忆时间轴</h3>
      <TimelineBlock :items="timeline" />
    </section>

    <JournalSection type="quote" title="分享文案" :text="record.share_text" />

    <van-button block type="primary" class="primary-btn" :loading="exporting" @click="exportImage">
      导出手账长图
    </van-button>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue'
import { showToast } from 'vant'
import html2canvas from 'html2canvas'
import JournalSection from './JournalSection.vue'
import PhotoFilmStrip from './PhotoFilmStrip.vue'
import StickerTag from './StickerTag.vue'
import TimelineBlock from './TimelineBlock.vue'

const props = defineProps({ record: { type: Object, required: true } })
const pageRef = ref(null)
const exporting = ref(false)
const layout = computed(() => props.record.hand_account_layout || {})
const timeline = computed(() => props.record.timeline_items?.length ? props.record.timeline_items : layout.value.timeline_items || [])
const sections = computed(() => props.record.section_blocks?.length ? props.record.section_blocks : layout.value.section_blocks || [])

async function exportImage() {
  if (!pageRef.value) return
  exporting.value = true
  try {
    const canvas = await html2canvas(pageRef.value, { backgroundColor: '#f8f1e7', scale: 2, useCORS: true })
    const link = document.createElement('a')
    link.download = `${props.record.title || '旅行手账'}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    showToast('长图已生成')
  } catch (error) {
    showToast('导出失败，请稍后重试')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.hand-page {
  display: grid;
  gap: 14px;
}

.cover {
  position: relative;
  padding: 24px 18px;
  min-height: 168px;
  border-radius: 18px;
  color: #fffaf1;
  background:
    linear-gradient(135deg, rgba(63, 53, 45, 0.18), rgba(63, 53, 45, 0.02)),
    linear-gradient(150deg, var(--color-primary-mist-blue), var(--color-soft-green) 52%, var(--color-memory-orange));
  box-shadow: var(--shadow-card);
}

.cover::after {
  content: "";
  position: absolute;
  right: 20px;
  bottom: 20px;
  width: 82px;
  height: 38px;
  border-bottom: 1px solid rgba(255, 250, 241, 0.55);
  border-radius: 50%;
}

.stamp {
  display: inline-flex;
  margin: 0 0 12px;
  padding: 3px 10px;
  border: 1px solid rgba(255, 250, 241, 0.42);
  border-radius: 999px;
  font-size: 12px;
}

h1 {
  margin: 0;
  font-size: 25px;
  line-height: 1.3;
}

.cover p:last-child {
  margin: 10px 0 0;
  opacity: 0.88;
}

.section-stack {
  display: grid;
  gap: 12px;
}

.timeline-card h3 {
  margin: 0 0 14px;
}
</style>
