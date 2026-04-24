<template>
  <div class="prompt-structure-guide" v-if="showGuide">
    <div class="guide-header">
      <span class="guide-title">Prompt 结构检查</span>
      <el-button size="small" text @click="showGuide = false">
        <el-icon><close /></el-icon>
      </el-button>
    </div>
    <div class="guide-items">
      <div
        v-for="item in guideItems"
        :key="item.key"
        :class="['guide-item', item.status]"
      >
        <el-icon v-if="item.status === 'pass'"><circle-check-filled /></el-icon>
        <el-icon v-else-if="item.status === 'warning'"><warning-filled /></el-icon>
        <el-icon v-else><circle-close-filled /></el-icon>
        <span class="item-label">{{ item.label }}</span>
        <span class="item-hint" v-if="item.hint">：{{ item.hint }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Close, CircleCheckFilled, WarningFilled, CircleCloseFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  content: string
}>()

const showGuide = computed(() => props.content.length > 0)

const guideItems = computed(() => {
  const content = props.content
  const items = []

  // 检查角色设定
  const hasRole = /角色|你是一个|你是|担任|假设你/i.test(content)
  items.push({
    key: 'role',
    label: '角色设定',
    status: hasRole ? 'pass' : 'warning',
    hint: hasRole ? '' : '建议添加角色定义，如"你是一位专业的..."'
  })

  // 检查任务描述
  const hasTask = /请|帮我|需要|任务|翻译|生成|分析/i.test(content)
  items.push({
    key: 'task',
    label: '任务描述',
    status: hasTask ? 'pass' : 'warning',
    hint: hasTask ? '' : '建议明确任务，如"请帮我翻译以下内容"'
  })

  // 检查约束条件
  const hasConstraint = /要求|约束|限制|必须|不要|避免/i.test(content)
  items.push({
    key: 'constraint',
    label: '约束条件',
    status: hasConstraint ? 'pass' : 'warning',
    hint: hasConstraint ? '' : '建议添加约束，如"要求简洁"、"限制在100字内"'
  })

  // 检查输出格式
  const hasFormat = /格式|JSON|列表|表格|输出|返回|结果/i.test(content)
  items.push({
    key: 'format',
    label: '输出格式',
    status: hasFormat ? 'pass' : 'warning',
    hint: hasFormat ? '' : '建议指定输出格式，如"以 JSON 格式返回"'
  })

  // 检查变量定义
  const hasVariables = /\{\{.*?\}\}/.test(content)
  items.push({
    key: 'variables',
    label: '变量使用',
    status: hasVariables ? 'pass' : 'info',
    hint: hasVariables ? '' : '使用 {{变量名}} 定义输入变量'
  })

  return items
})
</script>

<style scoped>
.prompt-structure-guide {
  background: #fffbeb;
  border: 1px solid #fbbf24;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 12px;
}
.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.guide-title {
  font-weight: 600;
  color: #92400e;
  font-size: 13px;
}
.guide-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.guide-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.guide-item.pass {
  background: #dcfce7;
  color: #166534;
}
.guide-item.warning {
  background: #fef3c7;
  color: #92400e;
}
.guide-item.info {
  background: #f0f9ff;
  color: #0369a1;
}
.item-label {
  font-weight: 500;
}
.item-hint {
  color: inherit;
  opacity: 0.8;
}
</style>