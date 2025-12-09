<template>
  <div class="variable-input-container">
    <div v-if="variables.length > 0" class="variables-list">
      <div 
        v-for="varName in variables" 
        :key="varName"
        class="variable-item"
      >
        <div class="variable-header">
          <div class="variable-label">
            <el-icon class="var-icon"><Ticket /></el-icon>
            <span class="var-name">{{ varName }}</span>
            <el-tag 
              v-if="getVarInfo(varName).type !== 'text'" 
              size="small" 
              :type="getVarTypeTagType(getVarInfo(varName).type)"
            >
              {{ getVarTypeLabel(getVarInfo(varName).type) }}
            </el-tag>
            <span v-if="getVarInfo(varName).required" class="required-star">*</span>
          </div>
          
          <!-- 切换输入类型按钮（仅非 select/number 类型显示） -->
          <div 
            v-if="!['select', 'number'].includes(getVarInfo(varName).type)"
            class="type-switch"
          >
            <span 
              :class="['switch-item', { active: inputType[varName] === 'text' }]"
              @click="setInputType(varName, 'text')"
            >文本</span>
            <span 
              :class="['switch-item', { active: inputType[varName] === 'file' }]"
              @click="setInputType(varName, 'file')"
            >文件</span>
          </div>
        </div>

        <!-- 文本输入 -->
        <div v-if="inputType[varName] === 'text'" class="input-wrapper">
          <!-- 下拉选择 -->
          <el-select
            v-if="getVarInfo(varName).type === 'select' && getVarInfo(varName).options.length > 0"
            v-model="variableValues[varName]"
            :placeholder="getVarInfo(varName).placeholder"
            @change="handleInput"
            class="variable-select"
          >
            <el-option
              v-for="opt in getVarInfo(varName).options"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
          <!-- 数字输入 -->
          <el-input-number
            v-else-if="getVarInfo(varName).type === 'number'"
            v-model.number="variableValues[varName]"
            :placeholder="getVarInfo(varName).placeholder"
            @change="handleInput"
            class="variable-number"
            controls-position="right"
          />
          <!-- 多行文本 -->
          <el-input
            v-else-if="getVarInfo(varName).type === 'textarea'"
            v-model="variableValues[varName]"
            :placeholder="getVarInfo(varName).placeholder"
            @input="handleInput"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 8 }"
            class="variable-textarea"
          />
          <!-- 单行文本（默认） -->
          <el-input
            v-else
            v-model="variableValues[varName]"
            :placeholder="getVarInfo(varName).placeholder"
            @input="handleInput"
            :type="getVarInfo(varName).type === 'textarea' ? 'textarea' : 'text'"
            :autosize="getVarInfo(varName).type === 'textarea' ? { minRows: 2, maxRows: 6 } : undefined"
            class="variable-input"
          />
          <!-- 必填标记 -->
          <span v-if="getVarInfo(varName).required" class="required-mark">*必填</span>
        </div>

        <!-- 文件上传 -->
        <div v-else class="file-upload-wrapper">
          <!-- 已上传的文件显示 -->
          <div v-if="fileVariables[varName]" class="uploaded-file">
            <div class="file-icon">
              <el-icon size="20" color="#67c23a"><Document /></el-icon>
            </div>
            <div class="file-details">
              <span class="file-name">{{ uploadedFiles[fileVariables[varName]]?.filename || '文件' }}</span>
              <span class="file-meta">{{ uploadedFiles[fileVariables[varName]]?.file_type }}</span>
            </div>
            <el-icon 
              class="remove-icon"
              @click="removeFile(varName)"
            ><Close /></el-icon>
          </div>

          <!-- 文件上传按钮 -->
          <el-upload
            v-else
            :action="`${API_BASE_URL}/api/files/upload`"
            :headers="{ Authorization: `Bearer ${getToken()}` }"
            :show-file-list="false"
            :on-success="(response: any) => handleUploadSuccess(varName, response)"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            accept="image/*,.txt,.md,.csv,.json,.xml,.pdf,.doc,.docx,.py,.js,.ts"
            class="file-uploader"
          >
            <el-button type="primary" plain>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
              </svg>
              上传文件
            </el-button>
          </el-upload>
          <div class="upload-hint">
            支持图片、文本、文档、代码文件（最大10MB）
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
      </svg>
      <p>
        在 Prompt 中使用 <code v-pre>{{变量名}}</code> 来添加变量<br/>
        <small style="color: #909399;">
          增强格式：<code v-pre>{{名称:类型:默认值:选项}}</code><br/>
          类型：text / textarea / number / select / file
        </small>
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
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Ticket, Document, Close } from '@element-plus/icons-vue'
import { type UploadedFileItem } from '@/api'
import { extractVariablesEnhanced, type VariableInfo } from '@/utils/markdown'

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

const props = defineProps<{
  variables: string[]
  content?: string  // Prompt 内容，用于解析增强变量
  modelValue?: Record<string, string>
  fileModelValue?: Record<string, number>
}>()

// 解析增强变量信息
const enhancedVariables = computed<VariableInfo[]>(() => {
  if (props.content) {
    return extractVariablesEnhanced(props.content)
  }
  // 兼容旧格式：转换简单变量名为 VariableInfo
  return props.variables.map(name => ({
    name,
    type: 'text' as const,
    defaultValue: '',
    options: [],
    required: false,
    placeholder: `请输入 ${name} 的值`
  }))
})

// 获取变量信息
function getVarInfo(varName: string): VariableInfo {
  return enhancedVariables.value.find(v => v.name === varName) || {
    name: varName,
    type: 'text',
    defaultValue: '',
    options: [],
    required: false,
    placeholder: `请输入 ${varName} 的值`
  }
}

// 获取变量类型标签
function getVarTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    'textarea': '多行',
    'number': '数字',
    'select': '选择',
    'file': '文件'
  }
  return labels[type] || type
}

// 获取变量类型标签颜色
function getVarTypeTagType(type: string): string {
  const types: Record<string, string> = {
    'textarea': 'info',
    'number': 'warning',
    'select': 'success',
    'file': ''
  }
  return types[type] || ''
}

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, string>]
  'update:fileModelValue': [value: Record<string, number>]
}>()

// 动态获取 token
const getToken = () => localStorage.getItem('ai_prompt_lab_token') || ''

// 变量值
const variableValues = ref<Record<string, string>>(props.modelValue || {})
const fileVariables = ref<Record<string, number>>(props.fileModelValue || {})

// 每个变量的输入类型（text 或 file）
const inputType = ref<Record<string, 'text' | 'file'>>({})

// 已上传的文件信息缓存
const uploadedFiles = ref<Record<number, UploadedFileItem>>({})

// 设置输入类型
function setInputType(varName: string, type: 'text' | 'file') {
  inputType.value[varName] = type
  
  // 切换到文本时，清除文件变量
  if (type === 'text') {
    delete fileVariables.value[varName]
    emit('update:fileModelValue', fileVariables.value)
  }
  // 切换到文件时，清除文本值
  else {
    variableValues.value[varName] = ''
    emit('update:modelValue', variableValues.value)
  }
}

// 文件上传成功
function handleUploadSuccess(varName: string, response: any) {
  if (response.code === 0) {
    const fileData = response.data
    
    // 保存文件 ID
    fileVariables.value[varName] = fileData.id
    emit('update:fileModelValue', fileVariables.value)
    
    // 缓存文件信息
    uploadedFiles.value[fileData.id] = fileData
    
    ElMessage.success(`文件 ${fileData.filename} 上传成功`)
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 文件上传失败
function handleUploadError(error: any) {
  console.error('上传失败:', error)
  ElMessage.error('文件上传失败')
}

// 上传前检查
function beforeUpload(file: File) {
  const maxSize = 10 * 1024 * 1024 // 10MB
  
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  
  return true
}

// 移除文件
function removeFile(varName: string) {
  delete fileVariables.value[varName]
  emit('update:fileModelValue', fileVariables.value)
}

// 监听 modelValue 的变化
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      variableValues.value = { ...variableValues.value, ...newValue }
    }
  },
  { deep: true }
)

// 监听 fileModelValue 的变化
watch(
  () => props.fileModelValue,
  (newValue) => {
    if (newValue) {
      fileVariables.value = { ...fileVariables.value, ...newValue }
    }
  },
  { deep: true }
)

// 初始化变量
watch(
  () => props.variables,
  (newVars) => {
    newVars.forEach(varName => {
      const varInfo = getVarInfo(varName)
      
      // 初始化输入类型（根据变量定义的类型）
      if (!(varName in inputType.value)) {
        inputType.value[varName] = varInfo.type === 'file' ? 'file' : 'text'
      }
      
      // 初始化变量值（使用默认值）
      if (!(varName in variableValues.value)) {
        variableValues.value[varName] = varInfo.defaultValue || ''
      }
    })

    // 移除不存在的变量
    Object.keys(variableValues.value).forEach(key => {
      if (!newVars.includes(key)) {
        delete variableValues.value[key]
        delete fileVariables.value[key]
        delete inputType.value[key]
      }
    })
    
    // 通知父组件初始值
    emit('update:modelValue', variableValues.value)
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
  Object.keys(fileVariables.value).forEach(key => {
    delete fileVariables.value[key]
  })
  emit('update:modelValue', variableValues.value)
  emit('update:fileModelValue', fileVariables.value)
}

function handleFill() {
  Object.keys(variableValues.value).forEach(key => {
    if (inputType.value[key] === 'text') {
      variableValues.value[key] = `示例${key}`
    }
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
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.75rem;
}

.variable-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
  padding: 1rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e1e4e8;
  transition: all 0.15s;
}

.variable-item:hover {
  border-color: #d1d5da;
  box-shadow: 0 1px 3px rgba(27, 31, 35, 0.05);
}

.variable-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e1e4e8;
}

.variable-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #24292e;
}

.var-icon {
  color: #0366d6;
  font-size: 16px;
}

.var-name {
  color: #24292e;
}

.required-star {
  color: #f56c6c;
  font-weight: bold;
}

.type-switch {
  display: flex;
  gap: 0;
  background: #f0f2f5;
  border-radius: 4px;
  padding: 2px;
}

.switch-item {
  padding: 4px 10px;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  border-radius: 3px;
  transition: all 0.15s;
}

.switch-item:hover {
  color: #409eff;
}

.switch-item.active {
  background: #409eff;
  color: white;
}

.input-wrapper {
  width: 100%;
  position: relative;
}

.variable-select {
  width: 100%;
}

.variable-number {
  width: 100%;
}

.variable-input :deep(.el-input__wrapper) {
  border-radius: 6px;
}

.required-mark {
  position: absolute;
  right: 8px;
  top: 8px;
  font-size: 12px;
  color: #f56c6c;
}

.variable-textarea :deep(.el-textarea__inner) {
  font-size: 14px;
  line-height: 1.6;
  padding: 10px 12px;
  border: 1px solid #d1d5da;
  border-radius: 6px;
  min-height: 80px;
  transition: all 0.15s;
  background: white;
  font-family: 'Consolas', 'Monaco', 'SF Mono', 'Courier New', monospace;
  box-shadow: none;
}

.variable-textarea :deep(.el-textarea__inner):hover {
  border-color: #a8adb3;
}

.variable-textarea :deep(.el-textarea__inner):focus {
  border-color: #0366d6;
  box-shadow: 0 0 0 3px rgba(3, 102, 214, 0.1);
}

.file-upload-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.uploaded-file {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border: 1px solid #86efac;
  border-radius: 8px;
  transition: all 0.2s;
}

.uploaded-file:hover {
  border-color: #4ade80;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1);
}

.file-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.file-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: #166534;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  font-size: 11px;
  color: #16a34a;
  text-transform: uppercase;
}

.remove-icon {
  width: 20px;
  height: 20px;
  padding: 4px;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s;
}

.remove-icon:hover {
  color: #ef4444;
  background: #fef2f2;
}

.file-uploader {
  width: 100%;
}

.file-uploader :deep(.el-upload) {
  width: 100%;
}

.file-uploader button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 12px 16px !important;
  border: 1px dashed #d1d5da !important;
  background: white !important;
  transition: all 0.15s !important;
  border-radius: 6px !important;
  font-weight: 500 !important;
  color: #0366d6 !important;
}

.file-uploader button:hover {
  border-color: #0366d6 !important;
  background: #f6f8fa !important;
}

.file-uploader button svg {
  width: 18px;
  height: 18px;
  color: #0366d6;
}

.upload-hint {
  font-size: 0.75rem;
  color: #6a737d;
  text-align: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
  color: #6a737d;
  background: #fafbfc;
  border-radius: 6px;
  border: 1px dashed #d1d5da;
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
  color: #d1d5da;
}

.empty-state p {
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.5;
}

.empty-state code {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85rem;
  background: #f6f8fa;
  padding: 3px 6px;
  border-radius: 3px;
  color: #0366d6;
  border: 1px solid #e1e4e8;
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

