<template>
  <aside 
    class="sidebar-container bg-zinc-50 dark:bg-zinc-950/50 border-r border-zinc-200 dark:border-zinc-800 transition-all duration-300 relative group"
    :class="{ 'w-64': !collapsed, 'w-16': collapsed }"
  >
    <!-- Toggle Button -->
    <button 
      @click="toggleCollapse"
      class="absolute -right-3 top-6 w-6 h-6 rounded-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 flex items-center justify-center text-zinc-400 hover:text-zinc-900 dark:hover:text-white shadow-sm z-10 opacity-0 group-hover:opacity-100 transition-opacity"
    >
      <el-icon :size="12"><component :is="collapsed ? 'ArrowRight' : 'ArrowLeft'" /></el-icon>
    </button>

    <div class="h-full flex flex-col">
      <!-- Header -->
      <div class="p-4 h-14 md:h-16 flex items-center shrink-0 overflow-hidden border-b border-zinc-100 dark:border-zinc-800/50">
        <el-icon v-if="icon" :size="18" class="text-zinc-900 dark:text-white shrink-0"><component :is="icon" /></el-icon>
        <h3 v-if="!collapsed" class="ml-3 text-[13px] font-bold text-zinc-900 dark:text-zinc-100 truncate tracking-tight uppercase">
          {{ title }}
        </h3>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto py-4 scrollbar-hide">
        <slot></slot>
      </div>

      <!-- Footer / Status -->
      <div v-if="!collapsed" class="p-4 border-t border-zinc-100 dark:border-zinc-800/50">
        <slot name="footer"></slot>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  title?: string
  icon?: string
  defaultCollapsed?: boolean
}>()

const collapsed = ref(props.defaultCollapsed || false)

function toggleCollapse() {
  collapsed.value = !collapsed.value
}
</script>

<style scoped>
.sidebar-container {
  height: 100%;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

:deep(.sidebar-nav-item) {
  display: flex;
  align-items: center;
  padding: 0.625rem 0.875rem;
  margin: 0.125rem 0.5rem;
  border-radius: 8px;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

:deep(.sidebar-nav-item:hover) {
  background-color: #f1f5f9;
  color: #0f172a;
}

:deep(.dark .sidebar-nav-item:hover) {
  background-color: #1e293b;
  color: #f8fafc;
}

:deep(.sidebar-nav-item.active) {
  background-color: #f1f5f9;
  color: #0f172a;
  font-weight: 600;
}

:deep(.dark .sidebar-nav-item.active) {
  background-color: #1e293b;
  color: #f8fafc;
}
</style>
