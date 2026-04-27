<template>
  <div 
    class="prompt-card-wrapper group bg-white dark:bg-zinc-900 border border-zinc-200/50 dark:border-zinc-800/50 rounded-[2rem] p-6 cursor-pointer transition-all duration-500 hover:shadow-premium hover:-translate-y-1.5 relative overflow-hidden"
    @click="handleClick"
  >
    <!-- Background Decor (Subtle Gradient) -->
    <div class="absolute -right-4 -top-4 w-24 h-24 bg-brand-accent/5 rounded-full blur-2xl group-hover:bg-brand-accent/10 transition-colors"></div>

    <div class="relative z-10 flex flex-col h-full">
      <div class="flex justify-between items-start gap-4 mb-4">
        <h3 class="text-lg font-black text-zinc-900 dark:text-white group-hover:text-brand-accent transition-colors truncate tracking-tight leading-tight">
          {{ prompt.title }}
        </h3>
        
        <div class="flex items-center shrink-0 opacity-0 group-hover:opacity-100 transition-all translate-y-1 group-hover:translate-y-0">
          <button 
            @click.stop="handleFavorite"
            class="w-8 h-8 rounded-full flex items-center justify-center hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-all"
            :class="prompt.is_favorite ? 'text-amber-500' : 'text-zinc-400'"
          >
            <el-icon :size="16"><StarFilled v-if="prompt.is_favorite" /><Star v-else /></el-icon>
          </button>
          <el-dropdown @command="handleCommand" trigger="click" @click.stop>
            <button class="w-8 h-8 rounded-full flex items-center justify-center hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-400 transition-all">
              <el-icon :size="16"><MoreFilled /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu class="studio-dropdown-premium">
                <el-dropdown-item command="edit"><el-icon :size="14"><Edit /></el-icon> 编辑</el-dropdown-item>
                <el-dropdown-item command="duplicate"><el-icon :size="14"><CopyDocument /></el-icon> 复制</el-dropdown-item>
                <el-dropdown-item command="versions"><el-icon :size="14"><Clock /></el-icon> 历史</el-dropdown-item>
                <el-dropdown-item command="delete" divided class="text-danger"><el-icon :size="14"><Delete /></el-icon> 删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <p class="text-sm font-medium text-zinc-500 dark:text-zinc-400 line-clamp-2 leading-relaxed mb-6 min-h-[40px]">
        {{ prompt.description || '暂无详细描述...' }}
      </p>

      <div class="flex flex-wrap gap-2 mb-6">
        <span 
          v-for="tag in prompt.tags?.slice(0, 3)" 
          :key="tag"
          class="px-3 py-1 rounded-full bg-zinc-50 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 text-[10px] font-black uppercase tracking-widest border border-zinc-100 dark:border-zinc-700/50"
        >
          {{ tag }}
        </span>
      </div>

      <div class="mt-auto flex items-center justify-between pt-4 border-t border-zinc-50 dark:border-zinc-800/50">
        <div class="flex items-center space-x-3">
          <div class="px-2.5 py-0.5 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-300 text-[9px] font-mono font-black uppercase tracking-tighter">
            v{{ prompt.version }}
          </div>
          <div v-if="prompt.is_public" class="flex items-center space-x-1.5 text-emerald-500 text-[9px] font-black uppercase tracking-widest">
            <div class="w-1 h-1 rounded-full bg-current"></div>
            <span>Public</span>
          </div>
        </div>
        <span class="text-[9px] font-bold text-zinc-400 uppercase tracking-tighter">{{ formatRelativeTime(prompt.updated_at) }}</span>
      </div>
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
