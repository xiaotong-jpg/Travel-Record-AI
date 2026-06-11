<template>
  <header class="app-header">
    <div class="header-copy">
      <p class="eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
    <div class="birds">⌁</div>
  </header>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: 'AI 旅行记忆' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' }
})
</script>

<style scoped>
.app-header {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 4px;
  color: var(--color-accent-gold);
  font-size: 12px;
}

h1 {
  margin: 0;
  font-size: 25px;
  line-height: 1.25;
}

p {
  margin: 8px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.7;
}

.birds {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: var(--color-primary-blue-deep);
  background: rgba(255, 250, 241, 0.58);
  box-shadow: var(--shadow-soft);
}
</style>
