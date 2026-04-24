<template>
  <div class="commit-history-container bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
    <div class="px-5 py-4 border-b border-zinc-100 dark:border-zinc-800 flex items-center justify-between bg-zinc-50/50 dark:bg-zinc-800/30">
      <div class="flex items-center space-x-2">
        <el-icon class="text-brand-500"><Clock /></el-icon>
        <span class="text-xs font-bold uppercase tracking-widest text-zinc-500">版本提交记录</span>
      </div>
      <button @click="loadCommits" :class="{ 'animate-spin': loading }" class="p-1 text-zinc-400 hover:text-brand-500 transition-colors">
        <el-icon :size="16"><Refresh /></el-icon>
      </button>
    </div>

    <div class="timeline-wrapper p-4 max-h-[500px] overflow-y-auto scrollbar-hide" v-loading="loading">
      <div v-if="commits.length === 0" class="py-12 text-center opacity-30">
        <el-icon :size="32"><Memo /></el-icon>
        <p class="mt-2 text-xs font-bold uppercase tracking-widest">暂无提交记录</p>
      </div>

      <div class="relative space-y-1">
        <div
          v-for="(commit, index) in commits"
          :key="commit.id"
          class="commit-item group flex items-start space-x-4 p-3 rounded-xl transition-all cursor-pointer border border-transparent"
          :class="selectedCommit?.id === commit.id ? 'bg-brand-50/50 dark:bg-brand-900/10 border-brand-200/50 dark:border-brand-800/30' : 'hover:bg-zinc-50 dark:hover:bg-zinc-800/50'"
          @click="handleSelectCommit(commit)"
        >
          <!-- Custom Dot & Line -->
          <div class="flex flex-col items-center pt-1.5 shrink-0">
            <div 
              class="w-2.5 h-2.5 rounded-full border-2 transition-colors shrink-0"
              :class="selectedCommit?.id === commit.id ? 'bg-brand-500 border-brand-200 dark:border-brand-800' : 'bg-zinc-200 dark:bg-zinc-700 border-white dark:border-zinc-900'"
            ></div>
            <div v-if="index < commits.length - 1" class="w-px flex-1 bg-zinc-100 dark:bg-zinc-800 my-1 min-h-[20px]"></div>
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex justify-between items-start mb-0.5">
              <span class="text-sm font-bold text-zinc-800 dark:text-zinc-200 truncate group-hover:text-brand-600 transition-colors">
                {{ commit.title }}
              </span>
              <span class="text-[10px] font-mono text-zinc-400 shrink-0 ml-4">{{ formatTime(commit.created_at) }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-500">
                {{ commit.id.toString().substring(0, 7) }}
              </span>
              <span v-if="index === 0" class="text-[9px] font-black text-emerald-500 uppercase tracking-tighter">Latest</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Simple Pagination -->
    <div class="px-4 py-3 bg-zinc-50/30 dark:bg-zinc-800/20 border-t border-zinc-100 dark:border-zinc-800 flex justify-center" v-if="total > pageSize">
      <el-pagination
        small
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Refresh, Clock, Memo } from '@element-plus/icons-vue'
import { getCommits } from '@/api/git'

const props = defineProps<{
  promptId: number
  branchId: number
}>()

const emit = defineEmits<{
  (e: 'select', commit: any): void
}>()

const commits = ref<any[]>([])
const selectedCommit = ref<any>(null)
const loading = ref(false)
const total = ref(0)
const pageSize = 20
const currentPage = ref(1)

const loadCommits = async () => {
  if (!props.branchId) return
  loading.value = true
  try {
    const res = await getCommits(props.promptId, props.branchId, currentPage.value, pageSize)
    commits.value = res.data?.items || []
    total.value = res.data?.total || 0
    if (commits.value.length > 0 && !selectedCommit.value) {
       // auto-select first one? maybe not.
    }
  } finally { loading.value = false }
}

const handleSelectCommit = (commit: any) => { selectedCommit.value = commit; emit('select', commit) }
const handlePageChange = (page: number) => { currentPage.value = page; loadCommits() }
const formatTime = (time: string) => {
  const d = new Date(time)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

watch(() => props.branchId, () => { currentPage.value = 1; loadCommits() })
onMounted(loadCommits)
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
:deep(.el-pagination) {
  --el-pagination-button-bg-color: transparent;
}
</style>
