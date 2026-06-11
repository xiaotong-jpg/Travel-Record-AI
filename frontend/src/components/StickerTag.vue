<template>
  <span class="sticker-tag">{{ label }}</span>
</template>

<script setup>
defineProps({ label: { type: String, required: true } })
</script>
