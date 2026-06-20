import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/DashboardView.vue')
        },
        {
          path: 'reports',
          name: 'Reports',
          component: () => import('../views/ReportListView.vue')
        },
        {
          path: 'reports/:id',
          name: 'ReportDetail',
          component: () => import('../views/ReportDetailView.vue')
        },
        {
          path: 'growth',
          name: 'GrowthTracking',
          component: () => import('../views/GrowthTrackingView.vue')
        },
        {
          path: 'subscription',
          name: 'Subscription',
          component: () => import('../views/SubscriptionView.vue')
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('../views/SettingsView.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router