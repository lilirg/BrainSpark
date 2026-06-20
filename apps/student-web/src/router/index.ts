import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/assessment/:id',
      name: 'Assessment',
      component: () => import('../views/AssessmentView.vue')
    },
    {
      path: '/result/:sessionId',
      name: 'Result',
      component: () => import('../views/ResultView.vue')
    }
  ]
})

export default router