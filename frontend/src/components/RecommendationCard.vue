<template>
  <article class="recommendation-card">
    <div>
      <p class="card-meta">{{ item.estimated_time || '慢慢走' }} · {{ item.crowd_level || '人流适中' }}</p>
      <h3>{{ item.name }}</h3>
      <p>{{ item.reason }}</p>
    </div>
    <div class="tag-row">
      <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
    </div>
    <div class="route-note">{{ item.route_tip }}</div>
    <div v-if="item.alternative" class="alt-note">替代路线：{{ item.alternative }}</div>
  </article>
</template>

<script setup>
defineProps({ item: { type: Object, required: true } })
</script>

<style scoped>
.recommendation-card {
  padding: 15px;
  border-radius: 14px;
  background: rgba(255, 250, 241, 0.8);
  border: 1px solid var(--color-line);
  box-shadow: var(--shadow-soft);
}

h3 {
  margin: 4px 0 8px;
  font-size: 18px;
}

p {
  margin: 0;
  color: #5b4e43;
  line-height: 1.75;
}

.route-note,
.alt-note {
  margin-top: 10px;
  padding: 10px;
  border-radius: 8px;
  color: #5d5147;
  background: rgba(143, 177, 183, 0.14);
  font-size: 13px;
  line-height: 1.65;
}

.alt-note {
  background: rgba(216, 154, 112, 0.12);
}
</style>
