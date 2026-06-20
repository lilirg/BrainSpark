import request from './request'
import type { ApiResponse } from '@brainspark/shared-types'

export interface Child {
  id: number
  name: string
  studentCode: string
  gender: string
  age: number
  grade: string
  className: string
  avatar: string
  totalAssessments: number
  lastAssessmentDate: string
  status: string
}

export interface CognitiveDimension {
  name: string
  score: number
  percentile: number
  level: string
  description: string
  suggestion: string
}

export interface ParentDashboard {
  child: Child
  pendingReports: number
  completedAssessments: number
  averageScore: number
  recentActivities: any[]
  cognitiveProfile: CognitiveDimension[]
}

export const parentApi = {
  getChildren: () => request.get<any, ApiResponse<Child[]>>('/parent/children'),
  getDashboard: (childId: number) => request.get<any, ApiResponse<ParentDashboard>>(`/parent/dashboard/${childId}`),
  getUsage: () => request.get<any, ApiResponse<any>>('/parent/usage'),
  updateSettings: (settings: any) => request.put('/parent/settings', settings)
}