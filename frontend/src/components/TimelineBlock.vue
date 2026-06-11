<template>
  <div class="timeline">
    <div v-for="(item, index) in items" :key="index" class="timeline-item">
      <span class="dot"></span>
      <div>
        <p class="time">{{ item.time || `片刻 ${index + 1}` }}</p>
        <h4>{{ item.title }}</h4>
        <p>{{ item.text }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ items: { type: Array, default: () => [] } })
</script>

<style scoped>
.timeline {
  display: grid;
  gap: 14px;
}

.timeline-item {
  position: relative;
  display: grid;
  grid-template-columns: 18px 1fr;
  gap: 8px;
}

.timeline-item::before {
  content: "";
  position: absolute;
  left: 6px;
  top: 18px;
  bottom: -14px;
  width: 1px;
  background: var(--color-line);
}

.timeline-item:last-child::before {
  display: none;
}

.dot {
  width: 13px;
  height: 13px;
  margin-top: 4px;
  border: 3px solid rgba(255, 250, 241, 0.9);
  border-radius: 50%;
  background: var(--color-accent-gold);
}

.time {
  margin: 0;
  color: var(--color-memory-orange);
  font-size: 12px;
}

h4 {
  margin: 2px 0 4px;
  font-size: 15px;
}

p {
  margin: 0;
  color: #5b4e43;
  font-size: 13px;
  line-height: 1.75;
}
</style>
