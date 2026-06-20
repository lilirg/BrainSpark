import request from './request'
import type { ApiResponse } from '@brainspark/shared-types'

export const adminApi = {
  getAssessments: () => request.get<any, ApiResponse<any[]>>('/admin/content/assessments'),
  updateAssessmentStatus: (id: number, status: string) =>
    request.put(`/admin/content/assessments/${id}/status`, { status }),
  getKnowledgeDocs: () => request.get<any, ApiResponse<any[]>>('/admin/knowledge/docs'),
  reindexKnowledge: () => request.post('/admin/knowledge/reindex'),
  getAnalytics: () => request.get<any, ApiResponse<any>>('/admin/analytics/dashboard'),
  getPartners: () => request.get<any, ApiResponse<any[]>>('/admin/partners'),
  createPartner: (data: any) => request.post('/admin/partners', data),
  sendNotification: (data: any) => request.post('/admin/notifications', data)
}