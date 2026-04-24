<template>
  <div class="prompt-list-page min-h-screen bg-white dark:bg-zinc-950 flex flex-col">
    <Header />
    
    <main class="flex-1 overflow-y-auto">
      <div class="max-w-[1200px] mx-auto px-6 py-8 md:py-12">
        
        <!-- Workspace Header -->
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
          <div class="space-y-1.5">
            <h1 class="text-3xl font-bold text-zinc-900 dark:text-zinc-100 tracking-tight">工作台</h1>
            <p class="text-sm text-zinc-500 font-medium">设计、测试与管理您的 AI 提示词资产</p>
          </div>
          <div class="flex items-center space-x-3">
            <el-button 
              type="primary" 
              size="large" 
              @click="createPrompt"
              class="h-10 px-6 rounded-lg font-bold bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-none shadow-sm"
            >
              <el-icon class="mr-2"><Plus /></el-icon>
              新建项目
            </el-button>
          </div>
        </div>

        <!-- Stats Overview -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
          <div 
            v-for="stat in statCards" 
            :key="stat.label"
            class="bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-100 dark:border-zinc-800 p-5 rounded-xl transition-all"
          >
            <div class="text-[10px] font-bold text-zinc-400 uppercase tracking-widest mb-1.5">{{ stat.label }}</div>
            <div class="text-2xl font-bold text-zinc-900 dark:text-white leading-none tracking-tight">{{ stat.value }}</div>
          </div>
        </div>

        <!-- Filters & Toolbar -->
        <div class="sticky top-[64px] z-40 mb-8 py-3 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md border-b border-zinc-100 dark:border-zinc-800">
          <div class="flex flex-col md:flex-row items-center justify-between gap-4">
            <div class="flex items-center space-x-3 w-full md:w-auto">
              <div class="relative flex-1 md:w-80">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索项目名称..."
                  class="studio-search"
                  clearable
                  @change="handleSearch"
                >
                  <template #prefix>
                    <el-icon :size="16" class="text-zinc-400"><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <button 
                @click="toggleFavorite"
                class="flex items-center space-x-2 px-4 h-10 rounded-lg border border-zinc-200 dark:border-zinc-800 transition-all font-bold text-xs"
                :class="showFavoriteOnly ? 'bg-amber-50 border-amber-200 text-amber-600' : 'bg-white dark:bg-zinc-900 text-zinc-500 hover:border-zinc-300'"
              >
                <el-icon :size="14"><StarFilled v-if="showFavoriteOnly" /><Star v-else /></el-icon>
                <span class="hidden sm:inline uppercase tracking-widest">收藏</span>
              </button>
            </div>

            <div class="flex items-center space-x-2">
              <div class="flex bg-zinc-100 dark:bg-zinc-900 rounded-lg p-1">
                <button 
                  v-for="v in ['grid', 'list']" 
                  :key="v"
                  @click="viewMode = v"
                  class="p-1.5 px-2 rounded-md transition-all"
                  :class="viewMode === v ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white shadow-sm' : 'text-zinc-400 hover:text-zinc-600'"
                >
                  <el-icon :size="14"><component :is="v === 'grid' ? 'Grid' : 'List'" /></el-icon>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Content Area -->
        <div v-loading="promptStore.loading" class="min-h-[400px]">
          <!-- Empty State -->
          <div v-if="!promptStore.loading && promptStore.prompts.length === 0" class="flex flex-col items-center justify-center py-32 text-center">
            <div class="w-16 h-16 mb-6 bg-zinc-100 dark:bg-zinc-900 rounded-2xl flex items-center justify-center text-zinc-300">
              <el-icon :size="32"><Memo /></el-icon>
            </div>
            <h3 class="text-lg font-bold text-zinc-900 dark:text-white mb-2">暂无实验项目</h3>
            <p class="text-sm text-zinc-500 mb-8 max-w-xs mx-auto">开启您的第一个 AI 提示词工程实验</p>
            <el-button type="primary" size="large" @click="createPrompt" class="rounded-lg px-8">
              立即创建
            </el-button>
          </div>

          <!-- Grid View -->
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
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

          <!-- Pagination -->
          <div v-if="promptStore.total > pageSize" class="mt-12 flex justify-center py-8">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="promptStore.total"
              layout="prev, pager, next"
              class="carbon-pagination"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePromptStore } from '@/store/prompt'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Star, StarFilled, Plus, Grid, List, Memo } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import PromptCard from '@/components/PromptCard.vue'
import { PromptItem } from '@/api'

const router = useRouter()
const promptStore = usePromptStore()

const searchKeyword = ref('')
const showFavoriteOnly = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const viewMode = ref('grid')

const statCards = computed(() => [
  { label: '项目总数', value: promptStore.total },
  { label: '星标收藏', value: promptStore.prompts.filter(p => p.is_favorite).length },
  { label: '公开分享', value: promptStore.prompts.filter(p => p.is_public).length },
  { label: '运行版本', value: promptStore.prompts.filter(p => p.version > 1).length }
])

onMounted(() => { loadPrompts() })
async function loadPrompts() { await promptStore.fetchPrompts({ skip: (currentPage.value - 1) * pageSize.value, limit: pageSize.value, search: searchKeyword.value || undefined, is_favorite: showFavoriteOnly.value || undefined }) }
function handleSearch() { currentPage.value = 1; loadPrompts() }
function toggleFavorite() { showFavoriteOnly.value = !showFavoriteOnly.value; currentPage.value = 1; loadPrompts() }
function handlePageChange() { loadPrompts(); window.scrollTo({ top: 0, behavior: 'smooth' }) }
function createPrompt() { router.push('/editor') }
function handlePromptClick(prompt: PromptItem) { router.push(`/editor/${prompt.id}`) }
async function handleToggleFavorite(id: number) { await promptStore.toggleFavorite(id) }
function handleEdit(id: number) { router.push(`/editor/${id}`) }
async function handleDuplicate(id: number) { 
  try {
    const fullPrompt = await promptStore.fetchPromptDetail(id)
    if (!fullPrompt) return
    const newPrompt = await promptStore.createPrompt({ title: `${fullPrompt.title} (Copy)`, content: fullPrompt.content, description: fullPrompt.description || '', tags: fullPrompt.tags || [], is_public: false })
    ElMessage.success('已创建副本')
    loadPrompts()
  } catch (e) { ElMessage.error('复制失败') }
}
function handleVersions(id: number) { router.push({ path: `/editor/${id}`, query: { showVersions: 'true' } }) }
async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要永久删除该提示词及其所有历史版本吗？', '删除确认', { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'error', customClass: 'carbon-message-box danger' })
    await promptStore.deletePrompt(id)
    loadPrompts()
  } catch { }
}
</script>

<style scoped>
:deep(.studio-search .el-input__wrapper) {
  border-radius: 10px;
  background-color: var(--bg-sidebar) !important;
  box-shadow: none !important;
  border: 1px solid var(--border-color) !important;
  height: 40px;
}
</style>
