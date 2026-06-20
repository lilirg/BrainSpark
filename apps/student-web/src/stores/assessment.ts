import { defineStore } from 'pinia'
import { ref } from 'vue'
import { assessmentApi } from '../apis/assessment'
import type { AssessmentTask } from '@brainspark/shared-types'

export const useAssessmentStore = defineStore('assessment', () => {
  const currentTask = ref<AssessmentTask | null>(null)
  const todayTasks = ref<AssessmentTask[]>([])
  const loading = ref(false)

  async function fetchTodayTasks() {
    loading.value = true
    try {
      const res = await assessmentApi.getTodayTasks()
      todayTasks.value = res.data
    } catch (e) {
      console.error('获取今日任务失败', e)
    } finally {
      loading.value = false
    }
  }

  async function startTask(taskId: number) {
    const res = await assessmentApi.getTask(taskId)
    currentTask.value = res.data
    return res.data
  }

  return { currentTask, todayTasks, loading, fetchTodayTasks, startTask }
})