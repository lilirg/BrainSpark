import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '数据看板' },
  },
  {
    path: '/class',
    name: 'Class',
    component: () => import('@/views/ClassManagement.vue'),
    meta: { title: '班级管理' },
  },
  {
    path: '/assessment',
    name: 'Assessment',
    component: () => import('@/views/AssessmentList.vue'),
    meta: { title: '测评管理' },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/ReportList.vue'),
    meta: { title: '报告查看' },
  },
  {
    path: '/students',
    name: 'Students',
    component: () => import('@/views/StudentProfile.vue'),
    meta: { title: '学生档案' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router