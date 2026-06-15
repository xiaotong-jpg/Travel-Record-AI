<template>
  <div v-if="images?.length" class="film-strip">
    <div v-for="(image, index) in images" :key="image + index" class="film-frame">
      <img :src="assetUrl(image)" alt="旅行照片" />
    </div>
  </div>
  <div v-else class="photo-placeholder">照片会像胶片一样贴在这里</div>
</template>

<script setup>
defineProps({ images: { type: Array, default: () => [] } })

function assetUrl(url) {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('data:')) return url
  if (url.startsWith('/uploads')) return url
  return `/uploads/${url.replace(/^\/+/, '')}`
}
</script>

<style scoped>
.film-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 8px;
  border-radius: 10px;
  background: rgba(65, 54, 44, 0.12);
}

.film-frame {
  aspect-ratio: 3 / 4;
  padding: 5px;
  border-radius: 6px;
  background: #fffaf1;
  box-shadow: 0 8px 18px rgba(73, 57, 42, 0.12);
  transform: rotate(-1deg);
}

.film-frame:nth-child(2n) {
  transform: rotate(1.5deg);
}

img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.photo-placeholder {
  padding: 22px;
  border: 1px dashed rgba(202, 164, 106, 0.45);
  border-radius: 10px;
  color: var(--color-muted);
  text-align: center;
  background: rgba(255, 250, 241, 0.48);
}
</style>
