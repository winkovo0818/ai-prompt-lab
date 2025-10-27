<template>
  <div 
    class="sidebar bg-gray-50 border-r border-gray-200 transition-all duration-300"
    :class="{ 'w-64': !collapsed, 'w-16': collapsed }"
  >
    <div class="p-4 flex items-center justify-between">
      <h3 v-if="!collapsed" class="text-sm font-semibold text-gray-700">{{ title }}</h3>
      <el-button 
        text 
        @click="toggleCollapse"
        :icon="collapsed ? 'Expand' : 'Fold'"
        circle
      />
    </div>

    <div class="px-2">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  title?: string
}>()

const collapsed = ref(false)

function toggleCollapse() {
  collapsed.value = !collapsed.value
}
</script>

<style scoped>
.sidebar {
  height: 100%;
  overflow-y: auto;
}
</style>

