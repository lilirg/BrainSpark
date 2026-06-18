import type { ApiResponse, PaginatedRequest, PaginatedResponse, User } from '@brainspark/shared-types'

// 默认 API 基础路径，Vite 项目可通过 import.meta.env.VITE_API_BASE_URL 覆盖
const API_BASE_URL = '/api/v1'

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  setToken(token: string) {
    this.token = token
  }

  clearToken() {
    this.token = null
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }
    return headers
  }

  private async request<T>(method: string, url: string, data?: any): Promise<ApiResponse<T>> {
    const options: RequestInit = {
      method,
      headers: this.getHeaders()
    }
    if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
      options.body = JSON.stringify(data)
    }

    const response = await fetch(`${this.baseURL}${url}`, options)
    return response.json() as Promise<ApiResponse<T>>
  }

  // ==================== 认证相关 ====================

  login(credentials: { username: string; password: string }) {
    return this.post<{ token: string; refreshToken: string; user: User }>('/auth/login', credentials)
  }

  refreshToken(refreshToken: string) {
    return this.post<{ token: string; refreshToken: string }>('/auth/refresh', { refreshToken })
  }

  logout() {
    return this.post<void>('/auth/logout')
  }

  getMe() {
    return this.get<User>('/auth/me')
  }

  // ==================== 用户管理 ====================

  getUsers(params: PaginatedRequest) {
    return this.get<PaginatedResponse<User>>('/users', { params })
  }

  getUser(id: string) {
    return this.get<User>(`/users/${id}`)
  }

  createUser(user: Partial<User>) {
    return this.post<User>('/users', user)
  }

  updateUser(id: string, user: Partial<User>) {
    return this.put<User>(`/users/${id}`, user)
  }

  deleteUser(id: string) {
    return this.delete<void>(`/users/${id}`)
  }

  // ==================== 学生管理 ====================

  getStudents(params: PaginatedRequest) {
    return this.get<PaginatedResponse<any>>('/students', { params })
  }

  getStudent(id: string) {
    return this.get<any>(`/students/${id}`)
  }

  createStudent(student: Partial<any>) {
    return this.post<any>('/students', student)
  }

  updateStudent(id: string, student: Partial<any>) {
    return this.put<any>(`/students/${id}`, student)
  }

  deleteStudent(id: string) {
    return this.delete<void>(`/students/${id}`)
  }

  // ==================== 班级管理 ====================

  getClasses(params: PaginatedRequest) {
    return this.get<PaginatedResponse<any>>('/classes', { params })
  }

  getClass(id: string) {
    return this.get<any>(`/classes/${id}`)
  }

  createClass(cls: Partial<any>) {
    return this.post<any>('/classes', cls)
  }

  updateClass(id: string, cls: Partial<any>) {
    return this.put<any>(`/classes/${id}`, cls)
  }

  deleteClass(id: string) {
    return this.delete<void>(`/classes/${id}`)
  }

  // ==================== 测评管理 ====================

  getAssessments(params: PaginatedRequest) {
    return this.get<PaginatedResponse<any>>('/assessments', { params })
  }

  getAssessment(id: string) {
    return this.get<any>(`/assessments/${id}`)
  }

  createAssessment(assessment: Partial<any>) {
    return this.post<any>('/assessments', assessment)
  }

  updateAssessment(id: string, assessment: Partial<any>) {
    return this.put<any>(`/assessments/${id}`, assessment)
  }

  deleteAssessment(id: string) {
    return this.delete<void>(`/assessments/${id}`)
  }

  // ==================== 测评结果 ====================

  getAssessmentResults(params: PaginatedRequest) {
    return this.get<PaginatedResponse<any>>('/assessment-results', { params })
  }

  getAssessmentResult(id: string) {
    return this.get<any>(`/assessment-results/${id}`)
  }

  // ==================== 报告管理 ====================

  getReports(params: PaginatedRequest) {
    return this.get<PaginatedResponse<any>>('/reports', { params })
  }

  getReport(id: string) {
    return this.get<any>(`/reports/${id}`)
  }

  createReport(report: Partial<any>) {
    return this.post<any>('/reports', report)
  }

  updateReport(id: string, report: Partial<any>) {
    return this.put<any>(`/reports/${id}`, report)
  }

  deleteReport(id: string) {
    return this.delete<void>(`/reports/${id}`)
  }

  // ==================== HTTP 方法封装 ====================

  private get<T>(url: string, options?: { params?: Record<string, any> }): Promise<ApiResponse<T>> {
    let queryString = ''
    if (options?.params) {
      const searchParams = new URLSearchParams()
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value))
        }
      })
      queryString = searchParams.toString()
    }
    const fullUrl = queryString ? `${url}?${queryString}` : url
    return this.request<T>('GET', fullUrl)
  }

  private post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>('POST', url, data)
  }

  private put<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', url, data)
  }

  private patch<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', url, data)
  }

  private delete<T>(url: string): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', url)
  }
}

export const apiClient = new ApiClient()
export default ApiClient