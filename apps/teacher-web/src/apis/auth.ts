import http from './request'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
}

export interface UserInfo {
  id: number
  username: string
  email: string
  realName: string
  avatar: string
  role: string
  status: string
}

export const authApi = {
  login(data: LoginRequest) {
    return http.post<LoginResponse>('/auth/login', data)
  },

  refresh(refreshToken: string) {
    return http.post<LoginResponse>('/auth/refresh', { refreshToken })
  },

  logout() {
    return http.post('/auth/logout')
  },

  getMe() {
    return http.get<UserInfo>('/auth/me')
  },
}