import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../apis/request'
import type { ApiResponse } from '@brainspark/shared-types'

export const useUserStore = defineStore('user', () => {
  const user = ref<any>(null)
  const token = ref(localStorage.getItem('accessToken') || '')

  async function login(username: string, password: string) {
    const res = await request.post<any, ApiResponse<any>>('/auth/login', { username, password })
    token.value = res.data.accessToken
    localStorage.setItem('accessToken', res.data.accessToken)
    localStorage.setItem('refreshToken', res.data.refreshToken)
    await fetchUser()
  }

  async function fetchUser() {
    const res = await request.get<any, ApiResponse<any>>('/auth/me')
    user.value = res.data
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }

  return { user, token, login, fetchUser, logout }
})