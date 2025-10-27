import { defineStore } from 'pinia'
import { ref } from 'vue'
import { promptAPI, PromptItem } from '@/api'
import { ElMessage } from 'element-plus'

export const usePromptStore = defineStore('prompt', () => {
  // 状态
  const prompts = ref<PromptItem[]>([])
  const currentPrompt = ref<PromptItem | null>(null)
  const total = ref(0)
  const loading = ref(false)

  // 搜索和过滤条件
  const searchKeyword = ref('')
  const filterTags = ref<string[]>([])
  const showFavoriteOnly = ref(false)

  // 获取 Prompt 列表
  async function fetchPrompts(params?: {
    skip?: number
    limit?: number
    search?: string
    is_favorite?: boolean
  }) {
    loading.value = true
    try {
      const response = await promptAPI.getList(params) as any
      prompts.value = response.data.items
      total.value = response.data.total
    } catch (error) {
      console.error('获取 Prompt 列表失败:', error)
      ElMessage.error('获取列表失败')
    } finally {
      loading.value = false
    }
  }

  // 获取 Prompt 详情
  async function fetchPromptDetail(id: number): Promise<PromptItem> {
    loading.value = true
    try {
      const response = await promptAPI.getDetail(id) as any
      currentPrompt.value = response.data
      return response.data
    } catch (error) {
      console.error('获取 Prompt 详情失败:', error)
      ElMessage.error('获取详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建 Prompt
  async function createPrompt(data: {
    title: string
    content: string
    description?: string
    tags?: string[]
    is_public?: boolean
  }): Promise<PromptItem> {
    try {
      const response = await promptAPI.create(data) as any
      ElMessage.success('创建成功')
      return response.data
    } catch (error) {
      console.error('创建 Prompt 失败:', error)
      ElMessage.error('创建失败')
      throw error
    }
  }

  // 更新 Prompt
  async function updatePrompt(id: number, data: any): Promise<PromptItem> {
    try {
      const response = await promptAPI.update(id, data) as any
      ElMessage.success('更新成功')

      // 更新列表中的项
      const index = prompts.value.findIndex(p => p.id === id)
      if (index !== -1) {
        prompts.value[index] = response.data
      }

      // 更新当前 Prompt
      if (currentPrompt.value?.id === id) {
        currentPrompt.value = response.data
      }

      return response.data
    } catch (error) {
      console.error('更新 Prompt 失败:', error)
      ElMessage.error('更新失败')
      throw error
    }
  }

  // 删除 Prompt
  async function deletePrompt(id: number) {
    try {
      await promptAPI.delete(id)
      ElMessage.success('删除成功')

      // 从列表中移除
      prompts.value = prompts.value.filter(p => p.id !== id)
      total.value--

      // 清除当前 Prompt
      if (currentPrompt.value?.id === id) {
        currentPrompt.value = null
      }
    } catch (error) {
      console.error('删除 Prompt 失败:', error)
      ElMessage.error('删除失败')
      throw error
    }
  }

  // 切换收藏
  async function toggleFavorite(id: number) {
    try {
      const response = await promptAPI.toggleFavorite(id) as any
      const isFavorite = response.data.is_favorite

      // 更新列表
      const index = prompts.value.findIndex(p => p.id === id)
      if (index !== -1) {
        prompts.value[index].is_favorite = isFavorite
      }

      // 更新当前 Prompt
      if (currentPrompt.value?.id === id) {
        currentPrompt.value.is_favorite = isFavorite
      }

      ElMessage.success(isFavorite ? '已收藏' : '已取消收藏')
    } catch (error) {
      console.error('切换收藏失败:', error)
      ElMessage.error('操作失败')
      throw error
    }
  }

  // 清空当前 Prompt
  function clearCurrentPrompt() {
    currentPrompt.value = null
  }

  // 设置搜索关键词
  function setSearchKeyword(keyword: string) {
    searchKeyword.value = keyword
  }

  // 设置标签过滤
  function setFilterTags(tags: string[]) {
    filterTags.value = tags
  }

  // 切换只显示收藏
  function toggleShowFavoriteOnly() {
    showFavoriteOnly.value = !showFavoriteOnly.value
  }

  return {
    prompts,
    currentPrompt,
    total,
    loading,
    searchKeyword,
    filterTags,
    showFavoriteOnly,
    fetchPrompts,
    fetchPromptDetail,
    createPrompt,
    updatePrompt,
    deletePrompt,
    toggleFavorite,
    clearCurrentPrompt,
    setSearchKeyword,
    setFilterTags,
    toggleShowFavoriteOnly
  }
})

