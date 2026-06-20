import request from './request'
import type { ApiResponse } from '@brainspark/shared-types'

export interface Report {
  id: number
  studentId: number
  studentName: string
  type: string
  title: string
  status: string
  pdfUrl: string
  shareCode: string
  createdAt: string
  updatedAt: string
}

export const reportApi = {
  getReports: (studentId: number, type?: string) =>
    request.get<any, ApiResponse<Report[]>>('/reports', { params: { studentId, type } }),
  getReport: (id: number) => request.get<any, ApiResponse<Report>>(`/reports/${id}`),
  shareReport: (id: number) => request.post<any, ApiResponse<{ shareCode: string }>>(`/reports/${id}/share`)
}