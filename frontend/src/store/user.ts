import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, UserInfo } from '@/api'
import { tokenStorage } from '@/utils/token'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string | null>(tokenStorage.getToken())
  const userInfo = ref<UserInfo | null>(tokenStorage.getUser())

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)

  // 登录
  async function login(username: string, password: string) {
    try {
      const response = await authAPI.login({ username, password })
      const { access_token, user } = response.data

      token.value = access_token
      userInfo.value = user

      tokenStorage.setToken(access_token)
      tokenStorage.setUser(user)

      return true
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  // 注册
  async function register(username: string, email: string, password: string) {
    try {
      const response = await authAPI.register({ username, email, password })
      const { access_token, user } = response.data

      token.value = access_token
      userInfo.value = user

      tokenStorage.setToken(access_token)
      tokenStorage.setUser(user)

      return true
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    }
  }

  // 登出
  function logout() {
    token.value = null
    userInfo.value = null
    tokenStorage.clear()
  }

  // 更新用户信息
  async function fetchUserInfo() {
    try {
      const response = await authAPI.getCurrentUser()
      userInfo.value = response.data
      tokenStorage.setUser(response.data)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
      throw error
    }
  }

  // 更新 API Key
  async function updateApiKey(apiKey: string) {
    try {
      await authAPI.updateApiKey(apiKey)
      if (userInfo.value) {
        userInfo.value.api_key = apiKey
        tokenStorage.setUser(userInfo.value)
      }
    } catch (error) {
      console.error('更新 API Key 失败:', error)
      throw error
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    register,
    logout,
    fetchUserInfo,
    updateApiKey
  }
})

