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
            <!-- 装饰性背景 -->
            <div class="empty-decoration">
              <div class="decoration-circle circle-1"></div>
              <div class="decoration-circle circle-2"></div>
              <div class="decoration-circle circle-3"></div>
            </div>
            
            <!-- 图标区域 -->
            <div class="empty-icon-wrapper">
              <div class="empty-icon-bg"></div>
              <div class="empty-icon">
                <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="12" y="8" width="56" height="64" rx="6" stroke="url(#gradient1)" stroke-width="3"/>
                  <path d="M24 24h32M24 36h24M24 48h28" stroke="url(#gradient1)" stroke-width="3" stroke-linecap="round"/>
                  <circle cx="56" cy="56" r="16" fill="url(#gradient2)"/>
                  <path d="M56 48v16M48 56h16" stroke="white" stroke-width="3" stroke-linecap="round"/>
                  <defs>
                    <linearGradient id="gradient1" x1="12" y1="8" x2="68" y2="72" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#3b82f6"/>
                      <stop offset="1" stop-color="#8b5cf6"/>
                    </linearGradient>
                    <linearGradient id="gradient2" x1="40" y1="40" x2="72" y2="72" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#3b82f6"/>
                      <stop offset="1" stop-color="#2563eb"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
            
            <h2 class="empty-title">开启你的 AI 创作之旅</h2>
            <p class="empty-description">
              创建你的第一个 Prompt 模板<br/>
              <span class="empty-hint">高效管理、快速调试、智能优化</span>
            </p>
            
            <el-button 
              type="primary" 
              size="large"
              @click="createPrompt"
              class="create-button"
            >
              <el-icon><Plus /></el-icon>
              创建第一个 Prompt
            </el-button>
            
            <div class="empty-tips">
              <div class="tip-item">
                <el-icon><Document /></el-icon>
                <span>支持变量模板</span>
              </div>
              <div class="tip-item">
                <el-icon><Star /></el-icon>
                <span>收藏常用 Prompt</span>
              </div>
              <div class="tip-item">
                <el-icon><Link /></el-icon>
                <span>一键分享协作</span>
              </div>
            </div>
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
import { Document, Star, Link, Clock, Plus, Search } from '@element-plus/icons-vue'
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
  overflow: hidden;
}

.content-container {
  flex: 1;
  overflow: hidden;
  width: 100%;
}

.main-content {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  padding: 24px 32px;
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
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  min-height: 200px;
}

@media (max-width: 1200px) {
  .prompts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .prompts-grid {
    grid-template-columns: 1fr;
  }
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
  min-height: calc(100vh - 340px);
  padding: 2rem;
}

.empty-content {
  text-align: center;
  max-width: 480px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  padding: 3rem 2.5rem;
  border-radius: 24px;
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.05),
    0 10px 40px -10px rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.1);
  position: relative;
  overflow: hidden;
}

/* 装饰性背景圆圈 */
.empty-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.5;
}

.circle-1 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
  top: -60px;
  right: -60px;
  animation: pulse-slow 4s ease-in-out infinite;
}

.circle-2 {
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%);
  bottom: -40px;
  left: -40px;
  animation: pulse-slow 5s ease-in-out infinite 1s;
}

.circle-3 {
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.06) 0%, transparent 70%);
  top: 50%;
  left: 10%;
  animation: pulse-slow 6s ease-in-out infinite 2s;
}

@keyframes pulse-slow {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.3;
  }
}

/* 图标包装器 */
.empty-icon-wrapper {
  position: relative;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1.5rem;
}

.empty-icon-bg {
  position: absolute;
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-radius: 50%;
  animation: float 4s ease-in-out infinite;
}

.empty-icon {
  position: relative;
  z-index: 1;
  width: 80px;
  height: 80px;
  animation: float 4s ease-in-out infinite;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 4px 8px rgba(59, 130, 246, 0.2));
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.75rem;
  position: relative;
  z-index: 1;
}

.empty-description {
  font-size: 0.95rem;
  color: #64748b;
  margin-bottom: 1.75rem;
  line-height: 1.8;
  position: relative;
  z-index: 1;
}

.empty-hint {
  color: #94a3b8;
  font-size: 0.85rem;
}

.create-button {
  font-size: 1rem;
  padding: 0.875rem 2rem;
  height: auto;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.35);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 1;
}

.create-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.45);
}

.create-button:active {
  transform: translateY(-1px);
}

.create-button :deep(.el-icon) {
  margin-right: 0.5rem;
}

/* 功能提示 */
.empty-tips {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(59, 130, 246, 0.1);
  position: relative;
  z-index: 1;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: #94a3b8;
  transition: all 0.2s;
}

.tip-item:hover {
  color: #3b82f6;
}

.tip-item .el-icon {
  font-size: 0.9rem;
  color: #3b82f6;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem !important;
  }
  
  .page-header .flex {
    flex-direction: column;
    align-items: stretch !important;
    gap: 1rem;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .create-btn {
    width: 100%;
    justify-content: center;
  }
  
  .toolbar {
    padding: 1rem;
  }
  
  .toolbar .flex {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .search-input {
    width: 100% !important;
  }
  
  .toolbar .space-x-2 {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .filter-btn {
    flex: 1;
    min-width: 0;
  }
  
  .prompts-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .pagination {
    padding: 1rem;
  }
  
  .pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .empty-content {
    padding: 2rem 1.5rem;
  }
  
  .empty-tips {
    flex-direction: column;
    gap: 0.75rem;
    align-items: center;
  }
}
</style>

