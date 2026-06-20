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
      component: () => import('../layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/dashboard' },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/DashboardView.vue')
        },
        {
          path: 'assessments',
          name: 'AssessmentManagement',
          component: () => import('../views/AssessmentManagement.vue')
        },
        {
          path: 'knowledge',
          name: 'KnowledgeManagement',
          component: () => import('../views/KnowledgeManagement.vue')
        },
        {
          path: 'partners',
          name: 'PartnerManagement',
          component: () => import('../views/PartnerManagement.vue')
        },
        {
          path: 'notifications',
          name: 'NotificationManagement',
          component: () => import('../views/NotificationManagement.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('accessToken')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router