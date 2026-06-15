import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
    { path: '/generate', name: 'Generate', component: () => import('../views/Generate.vue') },
    { path: '/chat-generate', name: 'ChatGenerate', component: () => import('../views/ChatGenerate.vue') },
    { path: '/recommend', name: 'Recommend', component: () => import('../views/Recommend.vue') },
    { path: '/memory', name: 'Memory', component: () => import('../views/Memory.vue') },
    { path: '/year-review', name: 'YearReview', component: () => import('../views/YearReview.vue'), meta: { tabbar: false } },
    { path: '/travel/:id', name: 'TravelDetail', component: () => import('../views/TravelDetail.vue'), meta: { tabbar: false } },
    { path: '/mine', name: 'Mine', component: () => import('../views/Mine.vue') }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
