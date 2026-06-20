import request from './request'
import type { ApiResponse, AssessmentTask, AssessmentResult } from '@brainspark/shared-types'

export const assessmentApi = {
  getTodayTasks: () => request.get<any, ApiResponse<AssessmentTask[]>>('/assessments/tasks/today'),
  getTask: (id: number) => request.get<any, ApiResponse<AssessmentTask>>(`/assessments/tasks/${id}`),
  createSession: (taskId: number) => request.post<any, ApiResponse<any>>('/assessments/sessions', { taskId }),
  submitResult: (sessionId: number, result: any) => request.post<any, ApiResponse<AssessmentResult>>(`/assessments/sessions/${sessionId}/result`, result)
}