<template>
  <div class="prompt-list-page min-h-screen bg-zinc-50 dark:bg-zinc-950 flex flex-col">
    <Header />
    
    <main class="flex-1 overflow-y-auto scrollbar-hide py-10 px-6">
      <div class="max-w-[1400px] mx-auto space-y-12">
        
        <!-- Welcome & Stats Section -->
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-10">
          <div class="space-y-2">
            <h1 class="text-4xl font-black text-zinc-900 dark:text-white tracking-tight">工作台 <span class="text-brand-accent">Workbench</span></h1>
            <p class="text-zinc-500 font-medium text-lg">设计、测试与管理您的 AI 提示词资产</p>
          </div>
          
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div 
              v-for="stat in statCards" 
              :key="stat.label"
              class="bg-white dark:bg-zinc-900 border border-zinc-200/50 dark:border-zinc-800/50 p-5 rounded-3xl shadow-premium flex flex-col justify-center min-w-[140px]"
            >
              <span class="text-[10px] font-black text-zinc-400 uppercase tracking-widest mb-1">{{ stat.label }}</span>
              <span class="text-2xl font-black text-zinc-900 dark:text-white leading-none">{{ stat.value }}</span>
            </div>
          </div>
        </div>

        <!-- Floating Glassmorphism Toolbar -->
        <div class="sticky top-0 z-40 py-4 -mx-2 px-2 pointer-events-none">
          <div class="max-w-4xl mx-auto bg-white/70 dark:bg-zinc-900/70 backdrop-blur-xl border border-white/20 dark:border-zinc-800/50 rounded-2xl p-2 shadow-modal flex items-center gap-3 pointer-events-auto">
            <div class="flex-1 relative">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索您的提示词项目..."
                class="studio-search-glass"
                clearable
                @change="handleSearch"
              >
                <template #prefix>
                  <el-icon :size="18" class="text-zinc-400"><Search /></el-icon>
                </template>
              </el-input>
            </div>
            
            <div class="h-8 w-px bg-zinc-200/50 dark:bg-zinc-800/50 mx-1"></div>
            
            <button 
              @click="toggleFavorite"
              class="flex items-center space-x-2 px-4 h-10 rounded-xl transition-all font-bold text-xs uppercase tracking-widest"
              :class="showFavoriteOnly ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/20' : 'text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800'"
            >
              <el-icon :size="14"><StarFilled v-if="showFavoriteOnly" /><Star v-else /></el-icon>
              <span class="hidden sm:inline">收藏</span>
            </button>

            <el-button 
              type="primary" 
              size="large" 
              @click="createPrompt"
              class="h-10 px-6 rounded-xl font-black bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-none shadow-premium text-xs uppercase tracking-widest"
            >
              <el-icon class="mr-2"><Plus /></el-icon>
              新建项目
            </el-button>
          </div>
        </div>

        <!-- Projects Grid -->
        <div v-loading="promptStore.loading" class="min-h-[400px]">
          <div v-if="!promptStore.loading && promptStore.prompts.length === 0" class="flex flex-col items-center justify-center py-40 text-center">
            <div class="w-20 h-20 mb-8 bg-white dark:bg-zinc-900 rounded-[2.5rem] shadow-premium flex items-center justify-center text-zinc-200">
              <el-icon :size="40"><Memo /></el-icon>
            </div>
            <h3 class="text-xl font-black text-zinc-900 dark:text-white mb-2 uppercase tracking-tight">一切准备就绪 Ready to Start</h3>
            <p class="text-zinc-500 font-medium mb-10 max-w-xs mx-auto">开启您的第一个 AI 提示词工程实验，探索智能的无限可能</p>
            <el-button type="primary" size="large" @click="createPrompt" class="rounded-2xl px-10 h-12 font-black shadow-premium">
              立即创建新项目
            </el-button>
          </div>

          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
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

          <!-- Refined Pagination -->
          <div v-if="promptStore.total > pageSize" class="mt-20 flex justify-center py-10">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="promptStore.total"
              layout="prev, pager, next"
              class="studio-pagination-premium"
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
import { Search, Star, StarFilled, Plus, Memo } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import PromptCard from '@/components/PromptCard.vue'
import { PromptItem } from '@/api'

const router = useRouter()
const promptStore = usePromptStore()

const searchKeyword = ref('')
const showFavoriteOnly = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
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
    await ElMessageBox.confirm('确定要永久删除该提示词及其所有历史版本吗？', '删除确认', { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'error', customClass: 'studio-message-box danger' })
    await promptStore.deletePrompt(id)
    loadPrompts()
  } catch { }
}
</script>

<style scoped>
.shadow-premium {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
}

.shadow-modal {
  box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.15), 0 18px 36px -18px rgba(0, 0, 0, 0.15);
}

:deep(.studio-search-glass .el-input__wrapper) {
  @apply bg-transparent !shadow-none border-none h-10 px-2;
}

:deep(.studio-search-glass .el-input__inner) {
  @apply text-sm font-bold text-zinc-900 dark:text-white placeholder:text-zinc-400;
}

:deep(.studio-pagination-premium) {
  --el-pagination-button-bg-color: #ffffff;
  --el-pagination-hover-color: var(--brand-accent);
}

.dark :deep(.studio-pagination-premium) {
  --el-pagination-button-bg-color: #18181b;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
