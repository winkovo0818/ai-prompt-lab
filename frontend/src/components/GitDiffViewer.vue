<template>
  <el-dialog 
    v-model="visible" 
    title="版本变更差异对比" 
    width="900px" 
    class="carbon-dialog"
    destroy-on-close
  >
    <template #header>
      <div class="flex items-center space-x-2">
        <el-icon class="text-brand-500"><Discount /></el-icon>
        <span class="text-lg font-bold tracking-tight text-zinc-900 dark:text-zinc-100">版本变更差异对比</span>
      </div>
    </template>

    <div class="diff-header-info grid grid-cols-[1fr,auto,1fr] items-center gap-4 mb-6">
      <div class="p-3 bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-800 rounded-xl flex flex-col min-w-0">
        <span class="text-[10px] font-black text-zinc-400 uppercase tracking-widest mb-1">源版本 (FROM)</span>
        <span class="text-sm font-bold text-zinc-700 dark:text-zinc-300 truncate">{{ fromCommit?.title || 'Loading...' }}</span>
      </div>
      <div class="w-8 h-8 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-400">
        <el-icon><ArrowRight /></el-icon>
      </div>
      <div class="p-3 bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-100 dark:border-emerald-800/30 rounded-xl flex flex-col min-w-0">
        <span class="text-[10px] font-black text-emerald-400 dark:text-emerald-500 uppercase tracking-widest mb-1">目标版本 (TO)</span>
        <span class="text-sm font-bold text-zinc-700 dark:text-zinc-200 truncate">{{ toCommit?.title || 'Loading...' }}</span>
      </div>
    </div>

    <!-- Statistics -->
    <div class="flex items-center space-x-4 mb-4 ml-1">
      <div class="flex items-center space-x-1.5 px-2 py-1 rounded-md bg-emerald-50 dark:bg-emerald-900/20 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-tight">
        <el-icon><Plus /></el-icon>
        <span>{{ diffResult?.additions || 0 }} 新增</span>
      </div>
      <div class="flex items-center space-x-1.5 px-2 py-1 rounded-md bg-rose-50 dark:bg-rose-900/20 text-[11px] font-bold text-rose-600 dark:text-rose-400 uppercase tracking-tight">
        <el-icon><Minus /></el-icon>
        <span>{{ diffResult?.deletions || 0 }} 移除</span>
      </div>
    </div>

    <!-- Diff Content Container -->
    <div class="diff-container bg-zinc-900 rounded-2xl overflow-hidden border border-zinc-800 shadow-xl" v-loading="loading">
      <div class="diff-code-area max-h-[500px] overflow-y-auto font-mono text-sm leading-relaxed p-4 scrollbar-hide">
        <div v-if="!loading && (!diffResult?.segments || diffResult.segments.length === 0)" class="py-20 text-center opacity-30 text-white">
          <p>未发现内容变更</p>
        </div>

        <div
          v-for="(segment, idx) in diffResult?.segments"
          :key="idx"
          :class="['diff-segment', segment.type]"
        >
          <div
            v-for="(line, lineIdx) in segment.lines"
            :key="lineIdx"
            class="diff-line group flex hover:bg-zinc-800 transition-colors"
            :class="{ 
              'bg-emerald-500/10 text-emerald-300': segment.type === 'added',
              'bg-rose-500/10 text-rose-300': segment.type === 'deleted',
              'text-zinc-400': segment.type === 'unchanged'
            }"
          >
            <div class="line-prefix w-8 shrink-0 flex items-center justify-center border-r border-white/5 opacity-50 select-none">
              {{ getLinePrefix(segment.type) }}
            </div>
            <div class="line-content px-4 py-0.5 whitespace-pre-wrap break-all flex-1 min-w-0 font-mono">
              {{ line }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end p-2">
        <el-button @click="visible = false" class="rounded-xl px-8 h-10 border-zinc-200 font-bold">关闭差异对比</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { getDiff } from '@/api/git'
import { Discount, ArrowRight, Plus, Minus } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: boolean
  promptId: number
  fromCommitId?: number
  toCommitId?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const visible = ref(false)
const loading = ref(false)
const fromCommit = ref<any>(null)
const toCommit = ref<any>(null)
const diffResult = ref<any>(null)

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.fromCommitId && props.toCommitId) loadDiff()
})

watch(visible, (val) => emit('update:modelValue', val))

const loadDiff = async () => {
  loading.value = true
  try {
    const res = await getDiff(props.promptId, props.fromCommitId!, props.toCommitId!)
    fromCommit.value = res.data?.from
    toCommit.value = res.data?.to
    diffResult.value = res.data?.diff
  } finally { loading.value = false }
}

const getLinePrefix = (type: string) => {
  if (type === 'added') return '+'
  if (type === 'deleted') return '-'
  return ' '
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
:deep(.carbon-dialog) {
  @apply rounded-3xl overflow-hidden !important;
}
:deep(.carbon-dialog .el-dialog__header) {
  @apply border-b border-zinc-100 dark:border-zinc-800 m-0 py-4 px-6;
}
:deep(.carbon-dialog .el-dialog__body) {
  @apply p-6;
}
:deep(.carbon-dialog .el-dialog__footer) {
  @apply border-t border-zinc-100 dark:border-zinc-800 p-4;
}

.diff-segment.added { @apply bg-emerald-500/5; }
.diff-segment.deleted { @apply bg-rose-500/5; }
</style>
