import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { aiConfigAPI, runAPI, type AIConfigResponse } from '@/api'

export interface AIConfig {
  id: number
  name: string
  baseUrl: string
  apiKey: string
  model: string
  description?: string
  isGlobal?: boolean
  isDefault?: boolean
}

export interface ModelConfig {
  id: string
  name: string
  description: string
  provider: string
  isCustom?: boolean
}

export const useConfigStore = defineStore('config', () => {
  // AI 配置列表
  const aiConfigs = ref<AIConfig[]>([])

  // 可用的模型列表（从用户配置动态加载）
  const availableModels = ref<ModelConfig[]>([])

  // 当前选择的模型
  const selectedModel = ref('gpt-3.5-turbo')

  // 模型参数
  const temperature = ref(0.7)
  const maxTokens = ref(2000)

  // 侧边栏折叠状态
  const sidebarCollapsed = ref(false)

  // 主题模式
  const darkMode = ref(false)

  // 自动从 localStorage 加载默认参数
  const initializeStore = () => {
    // 加载默认参数
    const savedParams = localStorage.getItem('ai-prompt-config')
    if (savedParams) {
      try {
        const params = JSON.parse(savedParams)
        if (params.temperature !== undefined) temperature.value = params.temperature
        if (params.maxTokens !== undefined) maxTokens.value = params.maxTokens
        if (params.selectedModel !== undefined) selectedModel.value = params.selectedModel
      } catch (e) {
        console.error('加载默认参数失败:', e)
      }
    }
  }

  // 立即初始化
  initializeStore()

  // 监听参数变化，自动保存（带防抖）
  let saveTimer: any = null
  watch([temperature, maxTokens, selectedModel], () => {
    clearTimeout(saveTimer)
    saveTimer = setTimeout(() => {
      saveDefaultParams()
      console.log('✅ 模型配置已自动保存')
    }, 500)
  })

  // 设置选择的模型
  function setSelectedModel(modelId: string) {
    selectedModel.value = modelId
  }

  // 设置温度
  function setTemperature(value: number) {
    temperature.value = value
  }

  // 设置最大 token 数
  function setMaxTokens(value: number) {
    maxTokens.value = value
  }

  // 切换侧边栏
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  // 切换主题
  function toggleDarkMode() {
    darkMode.value = !darkMode.value
    // 这里可以添加实际的主题切换逻辑
  }

  // AI 配置管理（调用后端 API）
  async function loadAIConfigs() {
    try {
      const response = await aiConfigAPI.getList()
      const configs = response.data as unknown as AIConfigResponse[]
      aiConfigs.value = configs.map((config: AIConfigResponse) => ({
        id: config.id,
        name: config.name,
        baseUrl: config.base_url,
        apiKey: config.api_key,
        model: config.model,
        description: config.description,
        isGlobal: config.is_global,
        isDefault: config.is_default
      }))
    } catch (error) {
      console.error('加载 AI 配置失败:', error)
      // 如果后端失败，尝试从 localStorage 加载
      const savedConfigs = localStorage.getItem('ai-configs')
      if (savedConfigs) {
        try {
          aiConfigs.value = JSON.parse(savedConfigs)
        } catch (e) {
          console.error('从 localStorage 加载失败:', e)
        }
      }
    }
  }

  // 加载用户配置的可用模型列表
  async function loadAvailableModels() {
    try {
      console.log('开始加载模型列表...')
      const response = await runAPI.getModels()
      console.log('API 响应:', response)
      const models = response.data as any[]
      
      console.log('加载的模型列表:', models)
      console.log('模型数量:', models?.length)
      
      if (models && models.length > 0) {
        availableModels.value = models.map(model => ({
          id: model.id,
          name: model.name,
          description: model.description || '',
          provider: model.provider || 'Custom'
        }))
        
        console.log('模型列表已更新:', availableModels.value)
        
        // 如果当前选择的模型不在列表中，选择第一个
        if (!models.find(m => m.id === selectedModel.value)) {
          selectedModel.value = models[0].id
          console.log('切换到默认模型:', selectedModel.value)
        }
      } else {
        console.warn('未找到配置的模型，请先在设置页面添加 AI 配置')
        // 提供一个默认的后备列表
        availableModels.value = [{
          id: 'not-configured',
          name: '请先配置 AI',
          description: '请到设置页面添加 AI 配置',
          provider: 'System'
        }]
      }
    } catch (error) {
      console.error('加载可用模型失败:', error) 
      // 提供后备列表
      availableModels.value = [{
        id: 'error',
        name: '加载失败',
        description: '请检查网络连接或刷新页面',
        provider: 'System'
      }]
    }
  }

  async function addAIConfig(config: Omit<AIConfig, 'id'>) {
    try {
      const response = await aiConfigAPI.create({
        name: config.name,
        base_url: config.baseUrl,
        api_key: config.apiKey,
        model: config.model,
        description: config.description
      })
      
      const data = response.data as unknown as AIConfigResponse
      const newConfig: AIConfig = {
        id: data.id,
        name: data.name,
        baseUrl: data.base_url,
        apiKey: data.api_key,
        model: data.model,
        description: data.description
      }
      
      aiConfigs.value.push(newConfig)
      saveToLocalStorage()
    } catch (error) {
      console.error('添加 AI 配置失败:', error)
      throw error
    }
  }

  async function updateAIConfig(id: number, config: Partial<AIConfig>) {
    try {
      const updateData: any = {}
      if (config.name !== undefined) updateData.name = config.name
      if (config.baseUrl !== undefined) updateData.base_url = config.baseUrl
      if (config.apiKey !== undefined) updateData.api_key = config.apiKey
      if (config.model !== undefined) updateData.model = config.model
      if (config.description !== undefined) updateData.description = config.description
      
      const response = await aiConfigAPI.update(id, updateData)
      const data = response.data as unknown as AIConfigResponse
      
      const index = aiConfigs.value.findIndex(c => c.id === id)
      if (index !== -1) {
        aiConfigs.value[index] = {
          id: data.id,
          name: data.name,
          baseUrl: data.base_url,
          apiKey: data.api_key,
          model: data.model,
          description: data.description
        }
        saveToLocalStorage()
      }
    } catch (error) {
      console.error('更新 AI 配置失败:', error)
      throw error
    }
  }

  async function deleteAIConfig(id: number) {
    try {
      await aiConfigAPI.delete(id)
      aiConfigs.value = aiConfigs.value.filter(c => c.id !== id)
      saveToLocalStorage()
    } catch (error) {
      console.error('删除 AI 配置失败:', error)
      throw error
    }
  }

  function saveToLocalStorage() {
    // 同时保存到 localStorage 作为备份
    localStorage.setItem('ai-configs', JSON.stringify(aiConfigs.value))
  }

  function saveDefaultParams() {
    // 保存默认参数到 localStorage
    localStorage.setItem('ai-prompt-config', JSON.stringify({
      temperature: temperature.value,
      maxTokens: maxTokens.value,
      selectedModel: selectedModel.value
    }))
  }

  return {
    aiConfigs,
    availableModels,
    selectedModel,
    temperature,
    maxTokens,
    sidebarCollapsed,
    darkMode,
    loadAIConfigs,
    addAIConfig,
    updateAIConfig,
    deleteAIConfig,
    saveDefaultParams,
    setSelectedModel,
    setTemperature,
    setMaxTokens,
    toggleSidebar,
    toggleDarkMode,
    loadAvailableModels
  }
})

