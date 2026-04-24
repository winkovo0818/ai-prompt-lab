<template>
  <div class="variable-input-container space-y-5 pb-10">
    <div v-if="variables.length > 0" class="flex flex-col space-y-5">
      <div 
        v-for="varName in variables" 
        :key="varName"
        class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 shadow-subtle group transition-all focus-within:border-zinc-400"
      >
        <div class="flex items-center justify-between mb-3 px-0.5">
          <div class="flex items-center space-x-2">
            <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">{{ varName }}</span>
            <span v-if="getVarInfo(varName).required" class="text-rose-500 font-bold">*</span>
            <el-tag v-if="getVarInfo(varName).type !== 'text'" size="small" effect="plain" class="rounded-md border-none bg-zinc-50 dark:bg-zinc-800 text-zinc-500 text-[9px] font-bold uppercase tracking-tighter">
              {{ getVarTypeLabel(getVarInfo(varName).type) }}
            </el-tag>
          </div>
          
          <div v-if="!['select', 'number'].includes(getVarInfo(varName).type)" class="flex bg-zinc-100 dark:bg-zinc-800 rounded-md p-0.5">
            <button 
              v-for="t in ['text', 'file']" 
              :key="t"
              @click="setInputType(varName, t as any)"
              class="px-2 py-0.5 text-[9px] font-bold uppercase rounded transition-all"
              :class="inputType[varName] === t ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm' : 'text-zinc-400 hover:text-zinc-500'"
            >
              {{ t === 'text' ? '文本' : '文件' }}
            </button>
          </div>
        </div>

        <!-- Inputs -->
        <div v-if="inputType[varName] === 'text'" class="relative">
          <el-select
            v-if="getVarInfo(varName).type === 'select'"
            v-model="variableValues[varName]"
            class="w-full carbon-input-clean"
            @change="handleInput"
          >
            <el-option v-for="opt in getVarInfo(varName).options" :key="opt" :label="opt" :value="opt" />
          </el-select>
          <el-input-number
            v-else-if="getVarInfo(varName).type === 'number'"
            v-model="variableValues[varName]"
            class="w-full carbon-input-clean"
            controls-position="right"
            @change="handleInput"
          />
          <el-input
            v-else
            v-model="variableValues[varName]"
            :type="getVarInfo(varName).type === 'textarea' ? 'textarea' : 'text'"
            :rows="3"
            :placeholder="getVarInfo(varName).placeholder"
            class="carbon-input-clean"
            @input="handleInput"
          />
        </div>

        <div v-else class="file-area">
          <div v-if="fileVariables[varName]" class="flex items-center justify-between p-2.5 bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/50 rounded-lg group/file">
            <div class="flex items-center space-x-2.5 overflow-hidden">
              <el-icon class="text-emerald-500 shrink-0"><Document /></el-icon>
              <span class="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 truncate">{{ uploadedFiles[fileVariables[varName]]?.filename }}</span>
            </div>
            <button @click="removeFile(varName)" class="p-1 hover:bg-emerald-100 dark:hover:bg-emerald-900 rounded text-emerald-400">
              <el-icon :size="12"><Close /></el-icon>
            </button>
          </div>
          
          <el-upload
            v-else
            :action="`${API_BASE_URL}/api/files/upload`"
            :headers="{ Authorization: `Bearer ${getToken()}` }"
            :show-file-list="false"
            :on-success="(res) => handleUploadSuccess(varName, res)"
            class="w-full"
          >
            <div class="w-full py-6 border border-dashed border-zinc-200 dark:border-zinc-800 rounded-lg flex flex-col items-center justify-center text-zinc-400 hover:border-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-all cursor-pointer">
              <el-icon :size="18"><UploadFilled /></el-icon>
              <span class="text-[9px] font-bold mt-2 uppercase tracking-widest">上传上下文文件</span>
            </div>
          </el-upload>
        </div>
      </div>
    </div>

    <div v-else class="flex flex-col items-center justify-center py-24 text-center opacity-40">
      <el-icon :size="32" class="text-zinc-300"><Tickets /></el-icon>
      <p class="mt-4 text-[10px] font-bold uppercase tracking-widest text-zinc-400">项目暂无变量</p>
    </div>

    <div v-if="variables.length > 0" class="flex space-x-2 pt-4">
      <el-button @click="handleClear" class="flex-1 rounded-lg h-9 text-[11px] font-bold uppercase tracking-wider border-zinc-200 dark:border-zinc-800">清空输入</el-button>
      <el-button type="primary" @click="handleFill" class="flex-1 rounded-lg h-9 text-[11px] font-bold uppercase tracking-wider bg-zinc-900 border-none shadow-sm">智能填充</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Tickets, Document, Close, UploadFilled } from '@element-plus/icons-vue'
import { extractVariablesEnhanced } from '@/utils/markdown'

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

const props = defineProps<{
  variables: string[]
  content?: string
  modelValue?: Record<string, string>
  fileModelValue?: Record<string, number>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, string>]
  'update:fileModelValue': [value: Record<string, number>]
}>()

const enhancedVariables = computed(() => props.content ? extractVariablesEnhanced(props.content) : [])
const getVarInfo = (name: string) => enhancedVariables.value.find(v => v.name === name) || { type: 'text', placeholder: `输入 ${name}...`, options: [], required: false }
const getVarTypeLabel = (type: string) => ({ textarea: '多行', number: '数值', select: '选择', file: '文件' }[type] || '文本')
const getToken = () => localStorage.getItem('ai_prompt_lab_token') || ''

const variableValues = ref<Record<string, string>>(props.modelValue || {})
const fileVariables = ref<Record<string, number>>(props.fileModelValue || {})
const inputType = ref<Record<string, 'text' | 'file'>>({})
const uploadedFiles = ref<Record<number, any>>({})

function setInputType(varName: string, type: 'text' | 'file') {
  inputType.value[varName] = type
  if (type === 'text') delete fileVariables.value[varName]
  else variableValues.value[varName] = ''
  emit('update:modelValue', variableValues.value)
  emit('update:fileModelValue', fileVariables.value)
}

function handleUploadSuccess(varName: string, response: any) {
  if (response.code === 0) {
    fileVariables.value[varName] = response.data.id
    uploadedFiles.value[response.data.id] = response.data
    emit('update:fileModelValue', fileVariables.value)
    ElMessage.success('文件上传成功')
  }
}

function removeFile(varName: string) {
  delete fileVariables.value[varName]
  emit('update:fileModelValue', fileVariables.value)
}

function handleInput() { emit('update:modelValue', variableValues.value) }
function handleClear() {
  props.variables.forEach(v => { variableValues.value[v] = ''; delete fileVariables.value[v] })
  emit('update:modelValue', variableValues.value)
  emit('update:fileModelValue', fileVariables.value)
}
function handleFill() {
  props.variables.forEach(v => { if (!variableValues.value[v]) variableValues.value[v] = `[${v} 示例内容]` })
  emit('update:modelValue', variableValues.value)
}

watch(() => props.variables, (newVars) => {
  newVars.forEach(v => {
    if (!inputType.value[v]) inputType.value[v] = getVarInfo(v).type === 'file' ? 'file' : 'text'
  })
}, { immediate: true })
</script>

<style scoped>
:deep(.carbon-input-clean .el-input__wrapper), 
:deep(.carbon-input-clean .el-textarea__inner),
:deep(.carbon-input-clean .el-input-number__increase),
:deep(.carbon-input-clean .el-input-number__decrease) {
  @apply rounded-lg bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 !shadow-none py-1.5;
}

:deep(.carbon-input-clean .el-textarea__inner) {
  @apply text-sm leading-relaxed;
}

:deep(.el-input-number.carbon-input-clean) {
  @apply w-full;
}
</style>
