<template>
  <section class="journal-section" :class="type">
    <p class="pin">{{ typeLabel }}</p>
    <h3>{{ title }}</h3>
    <p>{{ text }}</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, default: 'note' },
  title: { type: String, default: '手账便签' },
  text: { type: String, default: '' }
})

const typeLabel = computed(() => {
  const map = { note: '便签', journal: '日志', quote: '摘句' }
  return map[props.type] || '手账'
})
</script>

<style scoped>
.journal-section {
  position: relative;
  padding: 14px;
  border: 1px solid var(--color-line);
  border-radius: 10px;
  background: rgba(255, 250, 241, 0.75);
}

.journal-section.quote {
  background: rgba(216, 154, 112, 0.13);
}

.pin {
  display: inline-flex;
  margin: 0 0 8px;
  padding: 2px 8px;
  border-radius: 999px;
  color: #7a613f;
  background: rgba(202, 164, 106, 0.18);
  font-size: 12px;
}

h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

p {
  margin: 0;
  color: #5b4e43;
  line-height: 1.85;
  white-space: pre-line;
}
</style>
