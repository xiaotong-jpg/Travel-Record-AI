<template>
  <router-view />
  <van-tabbar v-if="showTabbar" route safe-area-inset-bottom active-color="#55777d" inactive-color="#9b8d81">
    <van-tabbar-item to="/" icon="wap-home-o">首页</van-tabbar-item>
    <van-tabbar-item to="/chat-generate" icon="chat-o">生成日志</van-tabbar-item>
    <van-tabbar-item to="/recommend" icon="guide-o">推荐</van-tabbar-item>
    <van-tabbar-item to="/memory" icon="notes-o">回忆</van-tabbar-item>
    <van-tabbar-item to="/mine" icon="user-o">我的</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const showTabbar = computed(() => route.meta.tabbar !== false)
</script>
