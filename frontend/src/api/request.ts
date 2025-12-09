import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 600000, // 5分钟超时（AI 调用可能需要较长时间）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加 token
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data

    // 统一响应格式处理
    // 兼容两种格式：{ code: 0, data, message } 或 { data, message }
    if (res.code === 0 || (res.data !== undefined && res.code === undefined)) {
      // 直接返回实际数据，而不是整个响应对象
      return { data: res.data, message: res.message }
    } else if (res.code !== undefined && res.code !== 0) {
      // 业务错误（有 code 且不为 0）
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    } else {
      // 其他情况直接返回
      return res
    }
  },
  (error) => {
    console.error('API 错误:', error.message)

    // 处理超时错误
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      ElMessage.error('请求超时，AI响应时间过长，请稍后重试或简化Prompt内容')
      return Promise.reject(error)
    }

    // 处理 HTTP 错误
    if (error.response) {
      const status = error.response.status
      const userStore = useUserStore()

      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          userStore.logout()
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('拒绝访问：权限不足')
          break
        case 404:
          // 优先使用后端返回的详细错误信息
          const notFoundMsg = error.response?.data?.detail || '请求的资源不存在'
          ElMessage.error(notFoundMsg)
          break
        case 429:
          ElMessage.warning({
            message: '请求过于频繁，请稍后再试',
            duration: 3000,
            showClose: true
          })
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        case 503:
          ElMessage.error('服务暂时不可用，请稍后重试')
          break
        default:
          const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || '请求失败'
          ElMessage.error(errorMsg)
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error(error.message || '请求失败')
    }

    return Promise.reject(error)
  }
)

export default request

