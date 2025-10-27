<template>
  <div class="variable-input-container">
    <div v-if="variables.length > 0" class="variables-list">
      <div 
        v-for="varName in variables" 
        :key="varName"
        class="variable-item"
      >
        <div class="variable-label">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.568 3H5.25A2.25 2.25 0 003 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 005.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 009.568 3z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 6h.008v.008H6V6z" />
          </svg>
          <span>{{ varName }}</span>
        </div>
        <el-input
          v-model="variableValues[varName]"
          :placeholder="`请输入 ${varName} 的值`"
          @input="handleInput"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 6 }"
          class="variable-textarea"
        />
      </div>
    </div>

    <div v-else class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
      </svg>
      <p>
        在 Prompt 中使用 <code v-pre>{{变量名}}</code> 来添加变量
      </p>
    </div>

    <div v-if="variables.length > 0" class="actions">
      <el-button @click="handleClear">
        清空
      </el-button>
      <el-button @click="handleFill" type="primary">
        填充示例
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  variables: string[]
  modelValue?: Record<string, string>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, string>]
}>()

// 变量值
const variableValues = ref<Record<string, string>>(props.modelValue || {})

// 监听 modelValue 的变化，更新本地值
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      // 合并新值，保留已有的值
      variableValues.value = { ...variableValues.value, ...newValue }
    }
  },
  { deep: true }
)

// 初始化变量值
watch(
  () => props.variables,
  (newVars) => {
    // 为新变量添加空值（但不覆盖已有值）
    newVars.forEach(varName => {
      if (!(varName in variableValues.value)) {
        variableValues.value[varName] = ''
      }
    })

    // 移除不存在的变量
    Object.keys(variableValues.value).forEach(key => {
      if (!newVars.includes(key)) {
        delete variableValues.value[key]
      }
    })
  },
  { immediate: true }
)

function handleInput() {
  emit('update:modelValue', variableValues.value)
}

function handleClear() {
  Object.keys(variableValues.value).forEach(key => {
    variableValues.value[key] = ''
  })
  emit('update:modelValue', variableValues.value)
}

function handleFill() {
  // 填充示例数据
  Object.keys(variableValues.value).forEach(key => {
    variableValues.value[key] = `示例${key}`
  })
  emit('update:modelValue', variableValues.value)
}
</script>

<style scoped>
.variable-input-container {
  padding: 0;
}

.variables-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.variable-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.variable-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  padding-left: 2px;
}

.variable-label svg {
  width: 16px;
  height: 16px;
  color: #3b82f6;
  flex-shrink: 0;
}

.variable-textarea :deep(.el-textarea__inner) {
  font-size: 14px;
  line-height: 1.6;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  min-height: 80px;
  transition: all 0.2s;
  background: white;
}

.variable-textarea :deep(.el-textarea__inner):hover {
  border-color: #cbd5e1;
}

.variable-textarea :deep(.el-textarea__inner):focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.variable-textarea :deep(.el-textarea__inner)::placeholder {
  color: #9ca3af;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: #9ca3af;
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
  color: #d1d5db;
}

.empty-state p {
  font-size: 0.875rem;
  margin: 0;
  line-height: 1.6;
}

.empty-state code {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.875rem;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  color: #3b82f6;
  font-weight: 500;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #f3f4f6;
}
</style>

