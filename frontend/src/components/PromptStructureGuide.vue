<template>
  <div class="prompt-structure-guide" v-if="showGuide">
    <div class="guide-header">
      <div class="flex items-center space-x-2">
        <el-icon class="text-zinc-900 dark:text-white"><InfoFilled /></el-icon>
        <span class="guide-title">Prompt 质量检查</span>
      </div>
      <button @click="showGuide = false" class="text-zinc-400 hover:text-zinc-600 transition-colors">
        <el-icon :size="14"><Close /></el-icon>
      </button>
    </div>
    <div class="guide-items">
      <div
        v-for="item in guideItems"
        :key="item.key"
        :class="['guide-item', item.status]"
      >
        <el-icon v-if="item.status === 'pass'" class="text-emerald-500"><CircleCheckFilled /></el-icon>
        <el-icon v-else-if="item.status === 'warning'" class="text-amber-500"><WarningFilled /></el-icon>
        <el-icon v-else class="text-zinc-300"><CircleCloseFilled /></el-icon>
        <span class="item-label">{{ item.label }}</span>
        <span class="item-hint" v-if="item.hint && item.status !== 'pass'">：{{ item.hint }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Close, CircleCheckFilled, WarningFilled, CircleCloseFilled, InfoFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  content: string
}>()

const showGuide = ref(true)

const guideItems = computed(() => {
  const content = props.content || ''
  const items = []

  const hasRole = /角色|你是一个|你是|担任|假设你|You are|Role/i.test(content)
  items.push({ key: 'role', label: '角色设定', status: hasRole ? 'pass' : 'warning', hint: '建议添加角色定义' })

  const hasTask = /请|帮我|需要|任务|翻译|生成|分析|Task|Please/i.test(content)
  items.push({ key: 'task', label: '任务描述', status: hasTask ? 'pass' : 'warning', hint: '建议明确任务目标' })

  const hasFormat = /格式|JSON|列表|表格|输出|返回|结果|Format|Output/i.test(content)
  items.push({ key: 'format', label: '输出规范', status: hasFormat ? 'pass' : 'warning', hint: '建议指定输出格式' })

  const hasVariables = /\{\{.*?\}\}/.test(content)
  items.push({ key: 'variables', label: '动态变量', status: hasVariables ? 'pass' : 'info', hint: '使用 {{变量}} 增强灵活性' })

  return items
})
</script>

<style scoped>
.prompt-structure-guide {
  @apply bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 shadow-subtle;
}
.guide-header {
  @apply flex justify-between items-center mb-4;
}
.guide-title {
  @apply font-bold text-zinc-900 dark:text-zinc-100 text-xs uppercase tracking-wider;
}
.guide-items {
  @apply flex flex-wrap gap-3;
}
.guide-item {
  @apply flex items-center gap-2 px-3 py-1.5 rounded-lg border border-zinc-100 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-[11px] font-medium transition-all;
}
.guide-item.pass { @apply border-emerald-100 dark:border-emerald-900/30 text-zinc-700 dark:text-zinc-300; }
.guide-item.warning { @apply border-amber-100 dark:border-amber-900/30 text-zinc-700 dark:text-zinc-300; }
.guide-item.info { @apply border-zinc-100 dark:border-zinc-800 text-zinc-500; }

.item-label { @apply font-bold; }
.item-hint { @apply opacity-60 font-normal; }
</style>
