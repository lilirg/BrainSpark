import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { UserInfo } from '@brainspark/shared-types'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null)
  const isAuthenticated = computed(() => !!userInfo.value)

  function setUser(info: UserInfo) {
    userInfo.value = info
  }

  function logout() {
    userInfo.value = null
  }

  return { userInfo, isAuthenticated, setUser, logout }
})