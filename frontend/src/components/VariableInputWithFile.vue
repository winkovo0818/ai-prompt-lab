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
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.568 3H5.25A2.25 2.25 0 003 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 005.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 009.568 3z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 6h.008v.008H6V6z" />
            </svg>
            <span>{{ varName }}</span>
          </div>
          
          <!-- 切换输入类型按钮 -->
          <el-button-group size="small">
            <el-button 
              :type="inputType[varName] === 'text' ? 'primary' : ''" 
              @click="setInputType(varName, 'text')"
            >
              文本
            </el-button>
            <el-button 
              :type="inputType[varName] === 'file' ? 'primary' : ''" 
              @click="setInputType(varName, 'file')"
            >
              文件
            </el-button>
          </el-button-group>
        </div>

        <!-- 文本输入 -->
        <div v-if="inputType[varName] === 'text'" class="input-wrapper">
          <el-input
            v-model="variableValues[varName]"
            :placeholder="`请输入 ${varName} 的值`"
            @input="handleInput"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 6 }"
            class="variable-textarea"
          />
        </div>

        <!-- 文件上传 -->
        <div v-else class="file-upload-wrapper">
          <!-- 已上传的文件显示 -->
          <div v-if="fileVariables[varName]" class="uploaded-file">
            <div class="file-info">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
              <span class="file-name">{{ uploadedFiles[fileVariables[varName]]?.filename || '文件' }}</span>
              <span class="file-type">{{ uploadedFiles[fileVariables[varName]]?.file_type }}</span>
            </div>
            <el-button 
              size="small" 
              type="danger" 
              @click="removeFile(varName)"
              text
            >
              移除
            </el-button>
          </div>

          <!-- 文件上传按钮 -->
          <el-upload
            v-else
            :action="`${API_BASE_URL}/files/upload`"
            :headers="{ Authorization: `Bearer ${token}` }"
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
import { ElMessage } from 'element-plus'
import { type UploadedFileItem } from '@/api'

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

const props = defineProps<{
  variables: string[]
  modelValue?: Record<string, string>
  fileModelValue?: Record<string, number>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, string>]
  'update:fileModelValue': [value: Record<string, number>]
}>()

// 获取 token
const token = localStorage.getItem('token')

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
      // 初始化输入类型
      if (!(varName in inputType.value)) {
        inputType.value[varName] = 'text'
      }
      
      // 初始化变量值
      if (!(varName in variableValues.value)) {
        variableValues.value[varName] = ''
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

.variable-label svg {
  width: 16px;
  height: 16px;
  color: #0366d6;
  flex-shrink: 0;
}

.input-wrapper {
  width: 100%;
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
  justify-content: space-between;
  padding: 10px 12px;
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  transition: all 0.15s;
}

.uploaded-file:hover {
  border-color: #d1d5da;
  background: #f3f4f6;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.file-info svg {
  width: 20px;
  height: 20px;
  color: #3b82f6;
  flex-shrink: 0;
}

.file-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-type {
  padding: 2px 8px;
  background: #dbeafe;
  color: #1e40af;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 4px;
  flex-shrink: 0;
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

