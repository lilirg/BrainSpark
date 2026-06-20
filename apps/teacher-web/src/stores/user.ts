import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type UserInfo } from '@/apis/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref<string | null>(localStorage.getItem('accessToken'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => user.value?.role || '')
  const username = computed(() => user.value?.realName || user.value?.username || '')

  async function login(username: string, password: string) {
    const res = await authApi.login({ username, password })
    const data = res.data
    token.value = data.accessToken
    refreshToken.value = data.refreshToken
    localStorage.setItem('accessToken', data.accessToken)
    localStorage.setItem('refreshToken', data.refreshToken)
    await fetchUserInfo()
  }

  async function fetchUserInfo() {
    try {
      const res = await authApi.getMe()
      user.value = res.data
    } catch {
      // 获取用户信息失败，清除登录状态
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }

  return {
    user,
    token,
    refreshToken,
    isLoggedIn,
    role,
    username,
    login,
    fetchUserInfo,
    logout,
  }
})