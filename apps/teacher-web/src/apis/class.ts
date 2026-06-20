import http from './request'

export interface ClassItem {
  id: number
  name: string
  grade: string
  description: string
  teacherId: number
  maxStudents: number
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface ClassRequest {
  name: string
  grade: string
  description?: string
  teacherId?: number
  maxStudents?: number
}

export const classApi = {
  getClasses(params?: { teacherId?: number; grade?: string; page?: number; size?: number }) {
    return http.get<{ content: ClassItem[] }>('/classes', { params })
  },

  getClass(id: number) {
    return http.get<ClassItem>(`/classes/${id}`)
  },

  createClass(data: ClassRequest) {
    return http.post<ClassItem>('/classes', data)
  },

  updateClass(id: number, data: ClassRequest) {
    return http.put<ClassItem>(`/classes/${id}`, data)
  },

  deleteClass(id: number) {
    return http.delete(`/classes/${id}`)
  },
}