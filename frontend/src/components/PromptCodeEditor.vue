<template>
  <div class="prompt-code-editor" :class="{ disabled, focused }">
    <div class="editor-wrapper">
      <!-- 背景高亮层 -->
      <div ref="highlightRef" class="highlight-backdrop" v-html="highlightedContent"></div>
      <!-- 实际输入框 -->
      <textarea
        ref="textareaRef"
        class="editor-textarea"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        @input="handleInput"
        @focus="focused = true"
        @blur="focused = false"
        @scroll="syncScroll"
        @keydown="handleKeyDown"
      ></textarea>
    </div>
    <div class="editor-status">
      <span class="status-hint">
        <span class="var-example" v-text="varSyntax"></span> 语法添加变量
      </span>
      <span class="status-info">
        {{ charCount }} 字符 · {{ variableCount }} 变量
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'

const props = defineProps<{
  modelValue: string
  placeholder?: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'input', value: string): void
}>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const highlightRef = ref<HTMLDivElement | null>(null)
const focused = ref(false)
const varSyntax = '{{变量}}'

const charCount = computed(() => props.modelValue?.length || 0)
const variableCount = computed(() => {
  const matches = props.modelValue?.match(/\{\{[^}]+\}\}/g)
  return matches ? matches.length : 0
})

const highlightedContent = computed(() => {
  if (!props.modelValue) return '<span class="placeholder-text">输入 Prompt 内容...</span>'
  
  let content = props.modelValue
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 高亮 {{变量}}
  content = content.replace(
    /(\{\{)([^}]+)(\}\})/g,
    '<span class="hl-var"><span class="hl-bracket">$1</span><span class="hl-name">$2</span><span class="hl-bracket">$3</span></span>'
  )
  
  content = content.replace(/\n/g, '<br>')
  return content
})

function handleInput(e: Event) {
  const target = e.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
  emit('input', target.value)
}

function syncScroll() {
  if (textareaRef.value && highlightRef.value) {
    highlightRef.value.scrollTop = textareaRef.value.scrollTop
  }
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Tab') {
    e.preventDefault()
    const textarea = textareaRef.value
    if (!textarea) return
    
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const value = props.modelValue || ''
    
    const newValue = value.substring(0, start) + '  ' + value.substring(end)
    emit('update:modelValue', newValue)
    
    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 2
    })
  }
}
</script>

<style scoped>
.prompt-code-editor {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.prompt-code-editor.focused {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.15);
}

.prompt-code-editor.disabled {
  background: #f5f7fa;
}

.editor-wrapper {
  position: relative;
  min-height: 280px;
}

.highlight-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 14px 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #303133;
  pointer-events: none;
  overflow-y: auto;
  overflow-x: hidden;
}

.editor-textarea {
  position: relative;
  width: 100%;
  min-height: 280px;
  padding: 14px 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.8;
  color: transparent;
  caret-color: #303133;
  background: transparent;
  border: none;
  outline: none;
  resize: vertical;
}

.editor-textarea::placeholder {
  color: #c0c4cc;
}

/* 高亮样式 */
.highlight-backdrop :deep(.placeholder-text) {
  color: #c0c4cc;
}

.highlight-backdrop :deep(.hl-var) {
  display: inline;
  background: linear-gradient(135deg, #ecf5ff 0%, #e6f1fc 100%);
  padding: 2px 0;
  border-radius: 4px;
}

.highlight-backdrop :deep(.hl-bracket) {
  color: #e6a23c;
  font-weight: 600;
}

.highlight-backdrop :deep(.hl-name) {
  color: #409eff;
  font-weight: 600;
  padding: 0 2px;
}

/* 底部状态栏 */
.editor-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
  font-size: 12px;
}

.status-hint {
  color: #909399;
}

.var-example {
  display: inline-block;
  background: #ecf5ff;
  color: #409eff;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-weight: 500;
}

.status-info {
  color: #c0c4cc;
}
</style>
