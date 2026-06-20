import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '数据看板', requiresAuth: true },
  },
  {
    path: '/class',
    name: 'Class',
    component: () => import('@/views/ClassManagement.vue'),
    meta: { title: '班级管理', requiresAuth: true },
  },
  {
    path: '/assessment',
    name: 'Assessment',
    component: () => import('@/views/AssessmentList.vue'),
    meta: { title: '测评管理', requiresAuth: true },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/ReportList.vue'),
    meta: { title: '报告查看', requiresAuth: true },
  },
  {
    path: '/students',
    name: 'Students',
    component: () => import('@/views/StudentProfile.vue'),
    meta: { title: '学生档案', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title} - BrainSpark 教师端`

  const token = localStorage.getItem('accessToken')
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router