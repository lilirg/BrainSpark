import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { UserInfo } from '@brainspark/shared-types'
import request from '../apis/request'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null)
  const isAuthenticated = computed(() => !!userInfo.value)

  function setUser(info: UserInfo) {
    userInfo.value = info
  }

  async function login(studentCode: string, password: string) {
    const res = await request.post<any, { code: number; data: { token: string; user: UserInfo }; message: string }>('/auth/login', {
      studentCode,
      password
    })
    if (res.data.token) {
      localStorage.setItem('accessToken', res.data.token)
    }
    userInfo.value = res.data.user
  }

  function logout() {
    userInfo.value = null
    localStorage.removeItem('accessToken')
  }

  return { userInfo, isAuthenticated, setUser, login, logout }
})