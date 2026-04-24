<template>
  <div 
    class="prompt-card-wrapper group bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-hidden cursor-pointer transition-all hover:border-zinc-400 dark:hover:border-zinc-600 hover:shadow-premium hover:-translate-y-0.5"
    @click="handleClick"
  >
    <!-- Header -->
    <div class="p-5 flex-1 flex flex-col">
      <div class="flex justify-between items-start mb-3">
        <h3 class="text-[14px] font-bold text-zinc-900 dark:text-white group-hover:text-brand-accent transition-colors line-clamp-1 tracking-tight leading-tight">
          {{ prompt.title }}
        </h3>
        <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            @click.stop="handleFavorite"
            class="p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-all"
            :class="prompt.is_favorite ? 'text-amber-500' : 'text-zinc-400'"
          >
            <el-icon :size="14"><StarFilled v-if="prompt.is_favorite" /><Star v-else /></el-icon>
          </button>
          <el-dropdown @command="handleCommand" trigger="click" @click.stop>
            <button class="p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-400 transition-all">
              <el-icon :size="14"><MoreFilled /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu class="carbon-dropdown-menu">
                <el-dropdown-item command="edit"><el-icon :size="14"><Edit /></el-icon> 编辑</el-dropdown-item>
                <el-dropdown-item command="duplicate"><el-icon :size="14"><CopyDocument /></el-icon> 复制</el-dropdown-item>
                <el-dropdown-item command="versions"><el-icon :size="14"><Clock /></el-icon> 历史</el-dropdown-item>
                <el-dropdown-item command="delete" divided class="text-danger"><el-icon :size="14"><Delete /></el-icon> 删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <p class="text-xs text-zinc-500 line-clamp-2 leading-relaxed mb-5 min-h-[32px]">
        {{ prompt.description || '暂无描述信息' }}
      </p>

      <!-- Tags -->
      <div class="flex flex-wrap gap-1.5 mb-2 mt-auto">
        <span 
          v-for="tag in prompt.tags?.slice(0, 3)" 
          :key="tag"
          class="px-2 py-0.5 rounded-md bg-zinc-50 dark:bg-zinc-800/50 text-zinc-500 dark:text-zinc-400 text-[10px] font-bold uppercase tracking-wider border border-zinc-100 dark:border-zinc-700/50 transition-colors"
        >
          {{ tag }}
        </span>
        <span v-if="prompt.tags && prompt.tags.length > 3" class="text-[10px] text-zinc-400 font-bold self-center ml-0.5">
          +{{ prompt.tags.length - 3 }}
        </span>
      </div>
    </div>

    <!-- Footer -->
    <div class="px-5 py-3 bg-zinc-50/30 dark:bg-zinc-950/30 border-t border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 text-[9px] font-mono font-bold">
          <span>V{{ prompt.version }}</span>
        </div>
        <div v-if="prompt.is_public" class="flex items-center space-x-1 text-emerald-600 dark:text-emerald-500 text-[9px] font-bold uppercase tracking-widest">
          <div class="w-1 h-1 rounded-full bg-current"></div>
          <span>公开</span>
        </div>
      </div>
      <span class="text-[9px] font-bold text-zinc-400 uppercase tracking-tight">{{ formatRelativeTime(prompt.updated_at) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PromptItem } from '@/api'
import { formatRelativeTime } from '@/utils/format'
import { Star, StarFilled, MoreFilled, Edit, CopyDocument, Clock, Delete } from '@element-plus/icons-vue'

const props = defineProps<{
  prompt: PromptItem
}>()

const emit = defineEmits<{
  click: [prompt: PromptItem]
  favorite: [id: number]
  edit: [id: number]
  duplicate: [id: number]
  versions: [id: number]
  delete: [id: number]
}>()

function handleClick() {
  emit('click', props.prompt)
}

function handleFavorite() {
  emit('favorite', props.prompt.id)
}

function handleCommand(command: string) {
  switch (command) {
    case 'edit': emit('edit', props.prompt.id); break
    case 'duplicate': emit('duplicate', props.prompt.id); break
    case 'versions': emit('versions', props.prompt.id); break
    case 'delete': emit('delete', props.prompt.id); break
  }
}
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

:deep(.carbon-dropdown-menu) {
  border-radius: 10px;
  padding: 4px;
  min-width: 140px;
}
</style>
