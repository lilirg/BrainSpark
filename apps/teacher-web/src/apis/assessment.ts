import http from './request'

export interface AssessmentType {
  id: number
  code: string
  name: string
  description: string
  category: string
  cognitiveDimension: string
  minAge: number
  maxAge: number
  durationSeconds: number
  isPublished: boolean
  status: string
}

export interface AssessmentTask {
  id: number
  title: string
  description: string
  typeCode: string
  difficulty: number
  durationMin: number
  classId: number
  startAt: string
  endAt: string
  status: string
  createdAt: string
}

export interface AssessmentTaskRequest {
  title: string
  description?: string
  typeCode: string
  config?: string
  difficulty?: number
  durationMin?: number
  classId?: number
  startAt?: string
  endAt?: string
}

export interface AssessmentResult {
  id: number
  userId: number
  taskId: number
  typeCode: string
  sessionId: string
  scoreData: string
  cognitiveProfile: string
  reportStatus: string
  status: string
  createdAt: string
}

export const assessmentApi = {
  // 测评类型
  getTypes(params?: { category?: string; status?: string; page?: number; size?: number }) {
    return http.get<{ content: AssessmentType[] }>('/assessments/types', { params })
  },

  getType(id: number) {
    return http.get<AssessmentType>(`/assessments/types/${id}`)
  },

  getTypeByCode(code: string) {
    return http.get<AssessmentType>(`/assessments/types/by-code/${code}`)
  },

  // 测评任务
  getTasks(params?: { classId?: number; typeCode?: string; status?: string; page?: number; size?: number }) {
    return http.get<{ content: AssessmentTask[] }>('/assessments/tasks', { params })
  },

  getTask(id: number) {
    return http.get<AssessmentTask>(`/assessments/tasks/${id}`)
  },

  createTask(data: AssessmentTaskRequest) {
    return http.post<AssessmentTask>('/assessments/tasks', data)
  },

  updateTask(id: number, data: AssessmentTaskRequest) {
    return http.put<AssessmentTask>(`/assessments/tasks/${id}`, data)
  },

  deleteTask(id: number) {
    return http.delete(`/assessments/tasks/${id}`)
  },

  updateTaskStatus(id: number, status: string) {
    return http.patch(`/assessments/tasks/${id}/status`, { status })
  },

  getTodayTasks() {
    return http.get<{ inProgress: number; completed: number }>('/assessments/tasks/today')
  },

  // 测评结果
  getResults(params?: { userId?: number; typeCode?: string; reportStatus?: string; page?: number; size?: number }) {
    return http.get<{ content: AssessmentResult[] }>('/assessments/results', { params })
  },

  getResult(id: number) {
    return http.get<AssessmentResult>(`/assessments/results/${id}`)
  },
}