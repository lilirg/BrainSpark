import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/assessment',
      name: 'Assessment',
      component: () => import('@/views/AssessmentView.vue'),
      children: [
        {
          path: ':taskId',
          name: 'AssessmentGame',
          component: () => import('@/views/AssessmentGameView.vue'),
        },
      ],
    },
    {
      path: '/report/:assessmentId',
      name: 'Report',
      component: () => import('@/views/ReportView.vue'),
    },
  ],
})

export default router