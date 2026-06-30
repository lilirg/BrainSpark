import request from './request'
import type { ApiResponse } from '@brainspark/shared-types'

export interface AssessmentItem {
  id: number
  name: string
  typeCode: string
  description: string
  durationMin: number
  difficulty: string
  status: string
  createdAt: string
}

export interface PartnerItem {
  id: number
  name: string
  contact: string
  phone: string
  email: string
  students: number
  status: string
  createdAt: string
}

export interface KnowledgeDoc {
  id: number
  title: string
  category: string
  status: string
  createdAt: string
  updatedAt: string
}

export const adminApi = {
  // 测评管理
  getAssessments: () => request.get<any, ApiResponse<AssessmentItem[]>>('/admin/content/assessments'),
  createAssessment: (data: Partial<AssessmentItem>) => request.post<any, ApiResponse<AssessmentItem>>('/admin/content/assessments', data),
  updateAssessment: (id: number, data: Partial<AssessmentItem>) => request.put<any, ApiResponse<AssessmentItem>>(`/admin/content/assessments/${id}`, data),
  deleteAssessment: (id: number) => request.delete(`/admin/content/assessments/${id}`),
  updateAssessmentStatus: (id: number, status: string) =>
    request.put(`/admin/content/assessments/${id}/status`, { status }),

  // 知识库管理
  getKnowledgeDocs: () => request.get<any, ApiResponse<KnowledgeDoc[]>>('/admin/knowledge/docs'),
  createKnowledgeDoc: (data: Partial<KnowledgeDoc>) => request.post<any, ApiResponse<KnowledgeDoc>>('/admin/knowledge/docs', data),
  updateKnowledgeDoc: (id: number, data: Partial<KnowledgeDoc>) => request.put<any, ApiResponse<KnowledgeDoc>>(`/admin/knowledge/docs/${id}`, data),
  deleteKnowledgeDoc: (id: number) => request.delete(`/admin/knowledge/docs/${id}`),
  reindexKnowledge: () => request.post('/admin/knowledge/reindex'),

  // 合作伙伴管理
  getPartners: () => request.get<any, ApiResponse<PartnerItem[]>>('/admin/partners'),
  createPartner: (data: Partial<PartnerItem>) => request.post<any, ApiResponse<PartnerItem>>('/admin/partners', data),
  updatePartner: (id: number, data: Partial<PartnerItem>) => request.put<any, ApiResponse<PartnerItem>>(`/admin/partners/${id}`, data),
  deletePartner: (id: number) => request.delete(`/admin/partners/${id}`),

  // 通知管理
  getNotifications: (params?: { page?: number; size?: number }) =>
    request.get<any, ApiResponse<{ content: any[]; total: number }>>('/admin/notifications', { params }),
  sendNotification: (data: any) => request.post('/admin/notifications', data),

  // 数据分析
  getAnalytics: () => request.get<any, ApiResponse<any>>('/admin/analytics/dashboard'),
  getDashboardStats: () => request.get<any, ApiResponse<{ totalUsers: number; totalAssessments: number; activePartners: number; revenue: number }>>('/admin/analytics/dashboard')
}