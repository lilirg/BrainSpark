import { defineStore } from 'pinia'
import { ref } from 'vue'
import { assessmentApi } from '../apis/assessment'
import type { AssessmentTask, AssessmentResult } from '@brainspark/shared-types'

export interface SessionData {
  sessionId: number
  taskId: number
  startTime: string
}

export const useAssessmentStore = defineStore('assessment', () => {
  const currentTask = ref<AssessmentTask | null>(null)
  const todayTasks = ref<AssessmentTask[]>([])
  const loading = ref(false)
  const currentSession = ref<SessionData | null>(null)
  const result = ref<AssessmentResult | null>(null)

  async function fetchTodayTasks() {
    loading.value = true
    try {
      const res = await assessmentApi.getTodayTasks()
      todayTasks.value = res.data ?? []
    } catch (e) {
      console.error('获取今日任务失败', e)
    } finally {
      loading.value = false
    }
  }

  async function startTask(taskId: number) {
    const res = await assessmentApi.getTask(taskId)
    currentTask.value = res.data ?? null
    
    // 创建测评会话
    const sessionRes = await assessmentApi.createSession(taskId)
    currentSession.value = {
      sessionId: sessionRes.data?.sessionId ?? Date.now(),
      taskId,
      startTime: new Date().toISOString()
    }
    
    return res.data
  }

  async function submitResult(sessionId: number, data: Record<string, unknown>) {
    const res = await assessmentApi.submitResult(sessionId, data)
    result.value = res.data ?? null
    return res.data
  }

  async function fetchResult(sessionId: number) {
    try {
      const res = await assessmentApi.getTodayTasks()
      return res.data
    } catch (e) {
      console.error('获取结果失败', e)
      return null
    }
  }

  function reset() {
    currentTask.value = null
    currentSession.value = null
    result.value = null
  }

  return {
    currentTask,
    todayTasks,
    loading,
    currentSession,
    result,
    fetchTodayTasks,
    startTask,
    submitResult,
    fetchResult,
    reset
  }
})