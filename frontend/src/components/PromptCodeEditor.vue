<template>
  <div class="prompt-code-editor-container h-full flex flex-col relative group" :class="{ disabled, focused }">
    <div class="editor-inner relative flex-1 flex overflow-hidden">
      <!-- Soft Line Numbers -->
      <div class="w-10 bg-transparent border-r border-zinc-100/50 dark:border-zinc-800/30 flex flex-col items-center py-4 text-[10px] font-mono text-zinc-200 dark:text-zinc-700 select-none shrink-0">
        <div v-for="i in lineCount" :key="i" class="leading-relaxed h-[1.8em]">{{ i }}</div>
      </div>

      <div class="flex-1 relative overflow-hidden">
        <!-- Syntax Layer -->
        <div 
          ref="highlightRef" 
          class="highlight-layer absolute inset-0 p-4 font-mono text-[13px] leading-relaxed whitespace-pre-wrap break-words pointer-events-none overflow-hidden text-transparent"
          v-html="highlightedContent"
        ></div>
        
        <!-- Editable Area -->
        <textarea
          ref="textareaRef"
          class="editor-textarea absolute inset-0 w-full h-full p-4 font-mono text-[13px] leading-relaxed bg-transparent text-zinc-800 dark:text-zinc-300 border-none outline-none resize-none caret-brand-accent overflow-y-auto scrollbar-hide"
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
    </div>
    
    <!-- Floating Minimal Status Indicators -->
    <div class="absolute bottom-4 right-4 flex items-center space-x-2 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300">
      <div class="px-2 py-1 rounded-full bg-white/80 dark:bg-zinc-800/80 backdrop-blur-md border border-zinc-100 dark:border-zinc-700 shadow-sm flex items-center space-x-1.5">
        <div class="w-1 h-1 rounded-full bg-brand-accent"></div>
        <span class="text-[9px] font-black text-zinc-500 uppercase tracking-widest">{{ variableCount }} Vars</span>
      </div>
      <div class="px-2 py-1 rounded-full bg-white/80 dark:bg-zinc-800/80 backdrop-blur-md border border-zinc-100 dark:border-zinc-700 shadow-sm">
        <span class="text-[9px] font-mono font-bold text-zinc-400 uppercase tracking-tighter">{{ cursorLine }}:{{ cursorCol }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'

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
const cursorLine = ref(1)
const cursorCol = ref(1)

const lineCount = computed(() => {
  const lines = (props.modelValue || '').split('\n').length
  return Math.max(lines, 15)
})

const variableCount = computed(() => {
  const matches = props.modelValue?.match(/\{\{[^}]+\}\}/g)
  return matches ? matches.length : 0
})

const highlightedContent = computed(() => {
  let content = props.modelValue || ''
  content = content.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  content = content.replace(
    /(\{\{)([^}]+)(\}\})/g,
    '<span class="hl-var-bracket">$1</span><span class="hl-var-name">$2</span><span class="hl-var-bracket">$3</span>'
  )
  return content + '\n'
})

function handleInput(e: Event) {
  const target = e.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
  emit('input', target.value)
  updateCursorPos()
}

function syncScroll() {
  if (textareaRef.value && highlightRef.value) {
    highlightRef.value.scrollTop = textareaRef.value.scrollTop
  }
}

function updateCursorPos() {
  const textarea = textareaRef.value
  if (!textarea) return
  const textBeforeCursor = textarea.value.substring(0, textarea.selectionStart)
  const lines = textBeforeCursor.split('\n')
  cursorLine.value = lines.length
  cursorCol.value = lines[lines.length - 1].length + 1
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
      updateCursorPos()
    })
  } else {
    setTimeout(updateCursorPos, 0)
  }
}

onMounted(() => {
  if (textareaRef.value) {
    textareaRef.value.addEventListener('click', updateCursorPos)
    textareaRef.value.addEventListener('keyup', updateCursorPos)
  }
})
</script>

<style scoped>
.editor-textarea {
  line-height: 1.8;
}

.highlight-layer {
  line-height: 1.8;
}

:deep(.hl-var-bracket) {
  @apply text-brand-accent font-bold opacity-30;
}

:deep(.hl-var-name) {
  @apply text-brand-accent font-bold underline decoration-brand-accent/20 underline-offset-4 opacity-100;
}

.disabled .editor-textarea {
  @apply opacity-70 cursor-not-allowed;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>