import { defineStore } from 'pinia'
import { ref } from 'vue'
import { assessmentApi, type AssessmentTask, type AssessmentType } from '@/apis/assessment'

export const useAssessmentStore = defineStore('assessment', () => {
  const tasks = ref<AssessmentTask[]>([])
  const types = ref<AssessmentType[]>([])
  const loading = ref(false)
  const totalTasks = ref(0)
  const todayStats = ref({ inProgress: 0, completed: 0 })

  async function fetchTasks(params?: { classId?: number; typeCode?: string; status?: string; page?: number; size?: number }) {
    loading.value = true
    try {
      const res = await assessmentApi.getTasks(params)
      tasks.value = res.data.content
      totalTasks.value = res.data.totalElements || 0
    } finally {
      loading.value = false
    }
  }

  async function fetchTypes(params?: { category?: string; status?: string }) {
    loading.value = true
    try {
      const res = await assessmentApi.getTypes(params)
      types.value = res.data.content
    } finally {
      loading.value = false
    }
  }

  async function createTask(data: { title: string; typeCode: string; classId?: number; durationMin?: number }) {
    const res = await assessmentApi.createTask(data)
    tasks.value.unshift(res.data)
    return res.data
  }

  async function updateTaskStatus(id: number, status: string) {
    await assessmentApi.updateTaskStatus(id, status)
    const task = tasks.value.find((t) => t.id === id)
    if (task) {
      task.status = status
    }
  }

  async function fetchTodayStats() {
    const res = await assessmentApi.getTodayTasks()
    todayStats.value = res.data
  }

  return {
    tasks,
    types,
    loading,
    totalTasks,
    todayStats,
    fetchTasks,
    fetchTypes,
    createTask,
    updateTaskStatus,
    fetchTodayStats,
  }
})