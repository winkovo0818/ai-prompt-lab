<template>
  <div class="prompt-list-page">
    <Header />
    
    <div class="content-container flex">
      <div class="main-content flex-1 p-6">
        <!-- 页面头部 -->
        <div class="page-header mb-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h1 class="text-2xl font-bold text-gray-900 mb-1">我的 Prompt</h1>
              <p class="text-sm text-gray-600">管理和组织你的 AI Prompt 模板</p>
            </div>
            <el-button type="primary" size="large" @click="createPrompt" class="create-btn">
              <el-icon><Plus /></el-icon>
              新建 Prompt
            </el-button>
          </div>

          <!-- 统计卡片 -->
          <div class="stats-grid mb-4">
            <div class="stat-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ promptStore.total }}</div>
                <div class="stat-label">总数</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ favoriteCount }}</div>
                <div class="stat-label">收藏</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                <el-icon><Link /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ publicCount }}</div>
                <div class="stat-label">公开</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ recentCount }}</div>
                <div class="stat-label">最近修改</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 工具栏 -->
        <div class="toolbar mb-6">
          <div class="flex items-center space-x-4">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索 Prompt..."
              class="search-input"
              clearable
              @change="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>

            <el-button
              :type="showFavoriteOnly ? 'primary' : 'default'"
              @click="toggleFavorite"
              class="filter-btn"
            >
              <el-icon><Star /></el-icon>
              {{ showFavoriteOnly ? '显示全部' : '仅显示收藏' }}
            </el-button>
          </div>
        </div>

        <div v-if="!promptStore.loading && promptStore.prompts.length === 0" class="empty-state">
          <div class="empty-content">
            <div class="empty-icon">
              <el-icon :size="80"><DocumentAdd /></el-icon>
            </div>
            <h2 class="empty-title">还没有 Prompt</h2>
            <p class="empty-description">创建你的第一个 AI Prompt，开始智能工作之旅</p>
            <el-button 
              type="primary" 
              size="large"
              @click="createPrompt"
              class="create-button"
            >
              <el-icon><Plus /></el-icon>
              创建第一个 Prompt
            </el-button>
          </div>
        </div>

        <div v-else v-loading="promptStore.loading" class="prompts-grid">
          <PromptCard
            v-for="prompt in promptStore.prompts"
            :key="prompt.id"
            :prompt="prompt"
            @click="handlePromptClick"
            @favorite="handleToggleFavorite"
            @edit="handleEdit"
            @duplicate="handleDuplicate"
            @delete="handleDelete"
            @versions="handleVersions"
          />
        </div>

        <div v-if="promptStore.total > pageSize" class="pagination mt-6 flex justify-center">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="promptStore.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePromptStore } from '@/store/prompt'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Star, Link, Clock, Plus, Search, DocumentAdd } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import PromptCard from '@/components/PromptCard.vue'
import { PromptItem } from '@/api'

const router = useRouter()
const promptStore = usePromptStore()

const searchKeyword = ref('')
const showFavoriteOnly = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)

// 统计数据
const favoriteCount = computed(() => {
  return promptStore.prompts.filter(p => p.is_favorite).length
})

const publicCount = computed(() => {
  return promptStore.prompts.filter(p => p.is_public).length
})

const recentCount = computed(() => {
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
  return promptStore.prompts.filter(p => new Date(p.updated_at) > sevenDaysAgo).length
})

onMounted(() => {
  loadPrompts()
})

async function loadPrompts() {
  await promptStore.fetchPrompts({
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value,
    search: searchKeyword.value || undefined,
    is_favorite: showFavoriteOnly.value || undefined
  })
}

function handleSearch() {
  currentPage.value = 1
  loadPrompts()
}

function toggleFavorite() {
  showFavoriteOnly.value = !showFavoriteOnly.value
  currentPage.value = 1
  loadPrompts()
}

function handlePageChange() {
  loadPrompts()
}

function handleSizeChange() {
  currentPage.value = 1
  loadPrompts()
}

function createPrompt() {
  router.push('/editor')
}

function handlePromptClick(prompt: PromptItem) {
  router.push(`/editor/${prompt.id}`)
}

async function handleToggleFavorite(id: number) {
  await promptStore.toggleFavorite(id)
}

function handleEdit(id: number) {
  router.push(`/editor/${id}`)
}

async function handleDuplicate(id: number) {
  try {
    const prompt = promptStore.prompts.find(p => p.id === id)
    if (!prompt) {
      ElMessage.error('找不到该 Prompt')
      return
    }
    
    // 复制 Prompt，标题添加 "副本" 后缀
    const newPromptData = {
      title: `${prompt.title} - 副本`,
      content: prompt.content,
      description: prompt.description || '',
      tags: prompt.tags || [],
      is_public: false // 副本默认为私有
    }
    
    const newPrompt = await promptStore.createPrompt(newPromptData)
    ElMessage.success('复制成功')
    
    // 刷新列表
    await loadPrompts()
    
    // 询问是否编辑新副本
    ElMessageBox.confirm('是否立即编辑新副本？', '提示', {
      confirmButtonText: '编辑',
      cancelButtonText: '稍后',
      type: 'success'
    }).then(() => {
      router.push(`/editor/${newPrompt.id}`)
    }).catch(() => {
      // 用户选择稍后
    })
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

function handleVersions(id: number) {
  // 跳转到编辑页面并自动打开版本历史
  router.push({
    path: `/editor/${id}`,
    query: { showVersions: 'true' }
  })
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这个 Prompt 吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await promptStore.deletePrompt(id)
    loadPrompts()
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.prompt-list-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.content-container {
  flex: 1;
  overflow: hidden;
}

.main-content {
  overflow-y: auto;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.main-content::-webkit-scrollbar {
  width: 10px;
}

.main-content::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.main-content::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 5px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* 页面头部 */
.page-header {
  margin-bottom: 1.5rem;
}

.create-btn {
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  transition: all 0.3s;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid #e5e7eb;
  transition: all 0.3s;
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

/* 工具栏 */
.toolbar {
  background: white;
  padding: 1.25rem 1.5rem;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.search-input {
  width: 320px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.2s;
}

.search-input :deep(.el-input__wrapper:hover),
.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-btn {
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s;
}

.filter-btn:hover {
  transform: translateY(-1px);
}

.prompts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  min-height: 200px;
}

.pagination {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.pagination :deep(.el-pagination) {
  gap: 0.5rem;
}

.pagination :deep(.el-pagination button),
.pagination :deep(.el-pager li) {
  border-radius: 8px;
  font-weight: 500;
}

.pagination :deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 300px);
  padding: 3rem;
}

.empty-content {
  text-align: center;
  max-width: 500px;
  background: white;
  padding: 4rem 3rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  margin-bottom: 2rem;
  color: #cbd5e0;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.empty-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.75rem;
}

.empty-description {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.create-button {
  font-size: 1rem;
  padding: 0.875rem 2rem;
  height: auto;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transition: all 0.3s;
}

.create-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}

.create-button :deep(.el-icon) {
  margin-right: 0.5rem;
}
</style>

