<template>
  <div class="result-viewer-container h-full flex flex-col bg-white dark:bg-zinc-950">
    <!-- Status Header -->
    <div v-if="result && !loading" class="px-5 py-3 bg-zinc-50 dark:bg-zinc-900 border-b border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
      <div class="flex items-center space-x-4 text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
        <div class="flex items-center space-x-1.5">
          <el-icon class="text-brand-accent"><Cpu /></el-icon>
          <span>{{ result.model }}</span>
        </div>
        <div class="flex items-center space-x-1.5">
          <el-icon class="text-emerald-500"><Timer /></el-icon>
          <span>{{ result.response_time }}s</span>
        </div>
      </div>
      
      <div class="flex items-center space-x-1">
        <button @click="copyResult" class="p-1.5 rounded-md hover:bg-white dark:hover:bg-zinc-800 text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors shadow-sm">
          <el-icon :size="14"><CopyDocument /></el-icon>
        </button>
        <button @click="showRenderedDialog" class="p-1.5 rounded-md hover:bg-white dark:hover:bg-zinc-800 text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors shadow-sm">
          <el-icon :size="14"><FullScreen /></el-icon>
        </button>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 relative overflow-hidden">
      <div v-if="loading" class="absolute inset-0 flex flex-col items-center justify-center p-12 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-sm z-10 animate-fade-in">
        <div class="w-10 h-10 rounded-xl bg-zinc-900 dark:bg-white flex items-center justify-center animate-pulse shadow-soft">
          <img src="/favicon.svg" alt="" class="w-5 h-5 invert dark:invert-0" />
        </div>
        <h4 class="mt-6 text-xs font-bold text-zinc-900 dark:text-white uppercase tracking-widest">AI 正在思考...</h4>
      </div>

      <div v-else-if="result" class="h-full overflow-y-auto p-6 scrollbar-hide">
        <!-- Cache Badge -->
        <div v-if="result.is_cached" class="mb-4 inline-flex items-center space-x-2 px-2 py-1 bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded text-[9px] text-zinc-500 font-bold uppercase tracking-tight">
          <el-icon><RefreshRight /></el-icon>
          <span>命中历史缓存</span>
        </div>

        <!-- Output Text -->
        <div class="output-wrapper bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-6 shadow-subtle min-h-[160px]">
          <pre class="font-mono text-[13px] leading-relaxed text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap break-words">{{ result.output }}</pre>
        </div>

        <!-- Meta Info -->
        <div class="mt-6 grid grid-cols-2 gap-4">
          <div class="p-4 bg-zinc-50 dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 flex flex-col">
            <span class="text-[9px] font-bold text-zinc-400 uppercase tracking-widest mb-1">Token 消耗</span>
            <span class="text-[15px] font-mono font-bold text-zinc-900 dark:text-zinc-100">{{ result.total_tokens }}</span>
          </div>
          <div class="p-4 bg-zinc-50 dark:bg-zinc-900 rounded-xl border border-zinc-100 dark:border-zinc-800 flex flex-col">
            <span class="text-[9px] font-bold text-zinc-400 uppercase tracking-widest mb-1">预估成本</span>
            <span class="text-[15px] font-mono font-bold text-zinc-900 dark:text-zinc-100">${{ result.cost.toFixed(5) }}</span>
          </div>
        </div>
      </div>

      <div v-else class="h-full flex flex-col items-center justify-center p-12 text-center opacity-30">
        <el-icon :size="40" class="text-zinc-300"><Document /></el-icon>
        <p class="mt-4 text-[10px] font-bold uppercase tracking-widest text-zinc-400">就绪</p>
      </div>
    </div>

    <!-- Fullscreen Render Modal -->
    <el-dialog
      v-model="renderedDialogVisible"
      title="预览渲染效果"
      fullscreen
      class="studio-full-dialog"
    >
      <div class="max-w-3xl mx-auto py-16 px-6">
        <div class="markdown-body p-10 bg-white dark:bg-zinc-900 rounded-2xl shadow-premium border border-zinc-200 dark:border-zinc-800" v-html="renderedOutput"></div>
      </div>
      <template #footer>
        <div class="flex items-center justify-center space-x-3 pb-10">
          <el-button @click="renderedDialogVisible = false" size="large" class="rounded-lg px-8">关闭</el-button>
          <el-button type="primary" @click="copyResult" size="large" class="rounded-lg px-8 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-none">复制原文</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { renderMarkdown } from '@/utils/markdown'
import { ElMessage } from 'element-plus'
import { Cpu, Timer, CopyDocument, FullScreen, RefreshRight, Document } from '@element-plus/icons-vue'

const props = defineProps<{
  result?: any
  loading?: boolean
  autoShowRendered?: boolean
}>()

const renderedDialogVisible = ref(false)
const renderedOutput = computed(() => props.result?.output ? renderMarkdown(props.result.output) : '')

watch(() => props.autoShowRendered, (newVal) => { if (newVal && props.result) renderedDialogVisible.value = true }, { immediate: true })

function showRenderedDialog() { renderedDialogVisible.value = true }
async function copyResult() {
  if (!props.result?.output) return
  try {
    await navigator.clipboard.writeText(props.result.output)
    ElMessage.success('已复制到剪贴板')
  } catch (error) { ElMessage.error('复制失败') }
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

:deep(.studio-full-dialog) {
  @apply bg-zinc-50 dark:bg-zinc-950 !important;
}

:deep(.studio-full-dialog .el-dialog__header) {
  @apply hidden;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
