<template>
  <div class="prompt-editor-page">
    <Header />
    
    <div class="editor-container">
      <div class="editor-main">
        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
              <span class="text-gray-400">|</span>
              <span class="text-sm text-gray-600">
                {{ isEditMode ? '编辑 Prompt' : '新建 Prompt' }}
              </span>
            </div>

            <div class="flex items-center space-x-2">
              <el-button 
                v-if="isEditMode" 
                @click="showExecutionHistory" 
                icon="List"
              >
                执行历史
              </el-button>
              <el-button 
                v-if="isEditMode" 
                @click="showVersionHistory" 
                icon="Clock"
              >
                版本历史
              </el-button>
              <el-button 
                v-if="isEditMode" 
                @click="handleDelete" 
                type="danger"
                icon="Delete"
              >
                删除
              </el-button>
              <el-button @click="handleSave" type="primary" :loading="saving">
                <el-icon><DocumentChecked /></el-icon>
                保存
              </el-button>
              <el-button @click="handleRun" type="success" :loading="running">
                <el-icon><CaretRight /></el-icon>
                运行
              </el-button>
            </div>
          </div>
        </div>

        <!-- 编辑区域 -->
        <div class="editor-content">
          <div class="editor-left">
            <div class="form-section">
              <el-form :model="formData" label-position="top">
                <el-form-item label="标题">
                  <el-input
                    v-model="formData.title"
                    placeholder="给你的 Prompt 起个名字"
                    size="large"
                  />
                </el-form-item>

                <el-form-item label="描述">
                  <el-input
                    v-model="formData.description"
                    type="textarea"
                    :rows="2"
                    placeholder="简单描述一下这个 Prompt 的用途"
                  />
                </el-form-item>

                <el-form-item label="Prompt 内容">
                  <el-input
                    v-model="formData.content"
                    type="textarea"
                    :rows="15"
                    placeholder="输入你的 Prompt，使用 {{变量名}} 来添加变量"
                    @input="handleContentChange"
                  />
                  <div class="text-xs text-gray-500 mt-1">
                    <span v-pre>提示：使用 {{变量名}} 语法添加可替换的变量</span>
                  </div>
                </el-form-item>

                <el-form-item label="标签">
                  <el-select
                    v-model="formData.tags"
                    multiple
                    filterable
                    allow-create
                    placeholder="添加标签"
                    class="w-full"
                  >
                    <el-option
                      v-for="tag in commonTags"
                      :key="tag"
                      :label="tag"
                      :value="tag"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item>
                  <el-checkbox v-model="formData.is_public">
                    公开分享（其他人可以查看）
                  </el-checkbox>
                </el-form-item>
              </el-form>
            </div>
          </div>

          <div class="editor-right">
            <el-tabs v-model="activeTab" class="h-full">
              <el-tab-pane label="变量配置" name="variables">
                <VariableInputWithFile
                  :variables="variables"
                  v-model="variableValues"
                  v-model:file-model-value="fileVariableValues"
                />
              </el-tab-pane>

              <el-tab-pane label="执行结果" name="result">
                <ResultViewer
                  :result="executionResult"
                  :loading="running"
                  :auto-show-rendered="autoShowRendered"
                />
              </el-tab-pane>

              <el-tab-pane label="模型配置" name="settings">
                <div class="settings-panel">
                  <el-form label-position="top">
                    <el-form-item label="模型">
                      <el-select v-model="configStore.selectedModel" class="w-full">
                        <el-option
                          v-for="model in configStore.availableModels"
                          :key="model.id"
                          :label="model.name"
                          :value="model.id"
                        >
                          <div>
                            <div>{{ model.name }}</div>
                            <div class="text-xs text-gray-500">{{ model.description }}</div>
                          </div>
                        </el-option>
                      </el-select>
                    </el-form-item>

                    <el-form-item label="Temperature">
                      <el-slider
                        v-model="configStore.temperature"
                        :min="0"
                        :max="2"
                        :step="0.1"
                        show-input
                      />
                    </el-form-item>

                    <el-form-item label="Max Tokens">
                      <el-input-number
                        v-model="configStore.maxTokens"
                        :min="100"
                        :max="128000"
                        :step="100"
                        class="w-full"
                      />
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </div>

    <!-- 版本历史抽屉 -->
    <el-drawer
      v-model="versionDrawerVisible"
      title="版本历史"
      direction="rtl"
      size="600px"
    >
      <div class="version-history-container">
        <el-timeline v-if="versions.length > 0">
          <el-timeline-item
            v-for="version in versions"
            :key="version.id"
            :timestamp="formatDate(version.created_at)"
            placement="top"
          >
            <el-card shadow="hover" class="version-card">
              <div class="version-header">
                <div class="version-info">
                  <span class="version-number">版本 {{ version.version }}</span>
                  <el-tag size="small" type="info" v-if="version.version === currentVersion">
                    当前版本
                  </el-tag>
                </div>
                <div class="version-actions">
                  <el-button 
                    size="small" 
                    @click="viewVersionContent(version)"
                    icon="View"
                  >
                    查看
                  </el-button>
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="restoreVersion(version)"
                    :disabled="version.version === currentVersion"
                    icon="RefreshLeft"
                  >
                    恢复
                  </el-button>
                </div>
              </div>
              <div class="version-summary">
                <div class="version-title">{{ version.title }}</div>
                <div class="version-change" v-if="version.change_summary">
                  变更：{{ version.change_summary }}
                </div>
                <div class="version-meta">
                  内容长度：{{ version.content.length }} 字符
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        
        <el-empty v-else description="暂无版本历史" />
      </div>
    </el-drawer>

    <!-- 版本内容查看对话框 -->
    <el-dialog
      v-model="versionContentVisible"
      :title="`版本 ${selectedVersion?.version} - ${selectedVersion?.title}`"
      width="80%"
      top="5vh"
    >
      <div v-if="selectedVersion" class="version-content-detail">
        <div class="version-meta-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="版本号">
              {{ selectedVersion.version }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(selectedVersion.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="标题" :span="2">
              {{ selectedVersion.title }}
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">
              {{ selectedVersion.description || '无' }}
            </el-descriptions-item>
            <el-descriptions-item label="变更摘要" :span="2">
              {{ selectedVersion.change_summary || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="version-content-preview">
          <h4>Prompt 内容</h4>
          <div class="content-box">
            <pre>{{ selectedVersion.content }}</pre>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="versionContentVisible = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="restoreVersion(selectedVersion!)"
          :disabled="selectedVersion?.version === currentVersion"
        >
          恢复到此版本
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行历史抽屉 -->
    <el-drawer
      v-model="executionHistoryDrawerVisible"
      title="执行历史"
      direction="rtl"
      size="700px"
    >
      <div class="execution-history-container">
        <div v-if="executionHistoryList.length > 0" class="history-list">
          <el-card 
            v-for="(history, index) in executionHistoryList" 
            :key="history.id"
            shadow="hover"
            class="history-card"
          >
            <div class="history-header">
              <div class="history-time">
                <el-icon><Clock /></el-icon>
                <span>{{ formatDate(history.created_at) }}</span>
              </div>
              <el-button 
                size="small" 
                type="primary"
                @click="viewExecutionHistory(history)"
              >
                查看结果
              </el-button>
            </div>
            
            <div class="history-info">
              <div class="info-row">
                <span class="label">模型:</span>
                <span class="value">{{ history.model }}</span>
              </div>
              <div class="info-row">
                <span class="label">Token:</span>
                <span class="value">{{ history.total_tokens }}</span>
              </div>
              <div class="info-row">
                <span class="label">成本:</span>
                <span class="value">${{ history.cost.toFixed(4) }}</span>
              </div>
              <div class="info-row">
                <span class="label">响应时间:</span>
                <span class="value">{{ history.response_time }}s</span>
              </div>
              <div v-if="history.variables && Object.keys(history.variables).length > 0" class="info-row">
                <span class="label">变量:</span>
                <span class="value">{{ JSON.stringify(history.variables) }}</span>
              </div>
            </div>
          </el-card>
        </div>
        
        <el-empty v-else description="暂无执行历史" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePromptStore } from '@/store/prompt'
import { useConfigStore } from '@/store/config'
import { runAPI, promptAPI, executionHistoryAPI } from '@/api'
import { extractVariables } from '@/utils/markdown'
import { ElMessage, ElMessageBox } from 'element-plus'
import Header from '@/components/Layout/Header.vue'
import VariableInputWithFile from '@/components/VariableInputWithFile.vue'
import ResultViewer from '@/components/ResultViewer.vue'

const route = useRoute()
const router = useRouter()
const promptStore = usePromptStore()
const configStore = useConfigStore()

const activeTab = ref('variables')
const saving = ref(false)
const running = ref(false)

const formData = reactive({
  title: '',
  content: '',
  description: '',
  tags: [] as string[],
  is_public: false
})

const variableValues = ref<Record<string, string>>({})
const fileVariableValues = ref<Record<string, number>>({})
const executionResult = ref<any>(null)

// 版本历史相关
const versionDrawerVisible = ref(false)
const versionContentVisible = ref(false)
const versions = ref<any[]>([])
const selectedVersion = ref<any>(null)
const currentVersion = ref<number>(0)

// 执行历史相关
const executionHistoryDrawerVisible = ref(false)
const executionHistoryList = ref<any[]>([])
const autoShowRendered = ref(false)

const commonTags = ['对话', '翻译', '写作', '代码', '分析', '创意', '教育', '商业']

const isEditMode = computed(() => !!route.params.id)
const variables = computed(() => extractVariables(formData.content))

// 获取当前Prompt的缓存key
const getCacheKey = () => {
  if (isEditMode.value) {
    return `prompt_variables_${route.params.id}`
  }
  return 'prompt_variables_new'
}

// 从 LocalStorage 加载变量值
function loadVariableValuesFromCache() {
  try {
    const cacheKey = getCacheKey()
    const cached = localStorage.getItem(cacheKey)
    if (cached) {
      const cachedData = JSON.parse(cached)
      console.log('📦 从缓存恢复变量值:', cachedData)
      
      // 兼容旧格式（直接是变量值对象）
      let cachedTextVars = cachedData.textVariables || cachedData
      let cachedFileVars = cachedData.fileVariables || {}
      
      // 只恢复当前 Prompt 中实际存在的变量
      const currentVars = variables.value
      const restoredTextValues: Record<string, string> = {}
      const restoredFileValues: Record<string, number> = {}
      
      currentVars.forEach(varName => {
        if (cachedTextVars[varName]) {
          restoredTextValues[varName] = cachedTextVars[varName]
        }
        if (cachedFileVars[varName]) {
          restoredFileValues[varName] = cachedFileVars[varName]
        }
      })
      
      if (Object.keys(restoredTextValues).length > 0) {
        variableValues.value = { ...variableValues.value, ...restoredTextValues }
        console.log('✅ 已恢复文本变量值')
      }
      
      if (Object.keys(restoredFileValues).length > 0) {
        fileVariableValues.value = { ...fileVariableValues.value, ...restoredFileValues }
        console.log('✅ 已恢复文件变量值')
      }
    }
  } catch (error) {
    console.error('恢复变量值失败:', error)
  }
}

// 保存变量值到 LocalStorage（防抖）
let saveTimer: any = null
function saveVariableValuesToCache() {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    try {
      const cacheKey = getCacheKey()
      const cacheData = {
        textVariables: variableValues.value,
        fileVariables: fileVariableValues.value
      }
      localStorage.setItem(cacheKey, JSON.stringify(cacheData))
      console.log('💾 变量值已缓存（文本+文件）')
    } catch (error) {
      console.error('保存变量值失败:', error)
    }
  }, 500)
}

// 监听变量值变化，自动保存（带防抖）
watch(variableValues, () => {
  saveVariableValuesToCache()
}, { deep: true })

// 监听文件变量值变化，自动保存
watch(fileVariableValues, () => {
  saveVariableValuesToCache()
}, { deep: true })

onMounted(async () => {
  try {
    await configStore.loadAvailableModels()
    console.log('✅ loadAvailableModels 完成')
  } catch (error) {
    console.error('❌ loadAvailableModels 失败:', error)
  }
  
  if (isEditMode.value) {
    await loadPrompt()
    
    // 加载完Prompt后，恢复变量缓存
    setTimeout(() => {
      loadVariableValuesFromCache()
    }, 100)
    
    // 检查是否需要自动打开版本历史
    if (route.query.showVersions === 'true') {
      await showVersionHistory()
    }
  }
})

async function loadPrompt() {
  const id = Number(route.params.id)
  try {
    const prompt = await promptStore.fetchPromptDetail(id)
    formData.title = prompt.title
    formData.content = prompt.content
    formData.description = prompt.description || ''
    formData.tags = prompt.tags || []
    formData.is_public = prompt.is_public
  } catch (error) {
    ElMessage.error('加载失败')
    router.push('/prompts')
  }
}

function handleContentChange() {
  // 内容变化时自动提取变量
}

async function handleSave() {
  if (!formData.title || !formData.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }

  saving.value = true
  try {
    if (isEditMode.value) {
      await promptStore.updatePrompt(Number(route.params.id), formData)
    } else {
      const newPrompt = await promptStore.createPrompt(formData)
      router.replace(`/editor/${newPrompt.id}`)
    }
  } catch (error) {
    // 错误已处理
  } finally {
    saving.value = false
  }
}

async function handleRun() {
  if (!formData.content) {
    ElMessage.warning('请输入 Prompt 内容')
    return
  }

  running.value = true
  executionResult.value = null
  autoShowRendered.value = false // 正常运行不自动弹框
  activeTab.value = 'result'

  try {
    const response = await runAPI.execute({
      prompt_id: isEditMode.value ? Number(route.params.id) : undefined,
      prompt_content: formData.content,
      variables: variableValues.value,
      file_variables: fileVariableValues.value,
      model: configStore.selectedModel,
      temperature: configStore.temperature,
      max_tokens: configStore.maxTokens
    })

    console.log('📊 执行结果响应:', response)
    // axios 拦截器返回的是 { data: ..., message: ... }
    executionResult.value = response.data
    console.log('✅ 结果已设置:', executionResult.value)
    
    // 执行成功后刷新历史记录列表
    if (isEditMode.value) {
      await loadExecutionHistory()
    }
  } catch (error) {
    console.error('❌ 执行失败:', error)
    ElMessage.error('执行失败')
  } finally {
    running.value = false
  }
}

function goBack() {
  router.push('/prompts')
}

// 删除 Prompt
async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个 Prompt 吗？此操作不可恢复，所有版本历史也会被删除。',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await promptStore.deletePrompt(Number(route.params.id))
    ElMessage.success('删除成功')
    router.push('/prompts')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      // 错误已在 store 中处理
    }
  }
}

// 版本历史相关函数
async function showVersionHistory() {
  if (!isEditMode.value) {
    ElMessage.warning('请先保存 Prompt')
    return
  }
  
  versionDrawerVisible.value = true
  await loadVersionHistory()
}

async function loadVersionHistory() {
  try {
    const response = await promptAPI.getVersions(Number(route.params.id)) as any
    versions.value = response.data.sort((a: any, b: any) => b.version - a.version)
    
    // 获取当前版本号（最大版本号）
    if (versions.value.length > 0) {
      currentVersion.value = Math.max(...versions.value.map((v: any) => v.version))
    }
    
    console.log('版本历史:', versions.value)
  } catch (error) {
    console.error('加载版本历史失败:', error)
    ElMessage.error('加载版本历史失败')
  }
}

function viewVersionContent(version: any) {
  selectedVersion.value = version
  versionContentVisible.value = true
}

async function restoreVersion(version: any) {
  if (!version) return
  
  try {
    await ElMessageBox.confirm(
      `确定要恢复到版本 ${version.version} 吗？当前未保存的修改将会丢失。`,
      '恢复版本',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 恢复表单数据
    formData.title = version.title
    formData.content = version.content
    formData.description = version.description || ''
    formData.tags = version.tags || []
    
    // 自动保存
    await handleSave()
    
    ElMessage.success('已恢复到该版本')
    versionContentVisible.value = false
    versionDrawerVisible.value = false
    
    // 重新加载版本历史
    await loadVersionHistory()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复版本失败:', error)
      ElMessage.error('恢复版本失败')
    }
  }
}

// 执行历史相关函数
async function showExecutionHistory() {
  if (!isEditMode.value) {
    ElMessage.warning('请先保存 Prompt')
    return
  }
  
  executionHistoryDrawerVisible.value = true
  await loadExecutionHistory()
}

async function loadExecutionHistory() {
  try {
    const response = await executionHistoryAPI.getList({
      prompt_id: Number(route.params.id),
      skip: 0,
      limit: 50
    }) as any
    executionHistoryList.value = response.data.items || []
    console.log('执行历史:', executionHistoryList.value)
  } catch (error) {
    console.error('加载执行历史失败:', error)
    ElMessage.error('加载执行历史失败')
  }
}

function viewExecutionHistory(history: any) {
  // 将历史结果显示到结果查看器
  executionResult.value = {
    prompt_title: formData.title,
    prompt_content: history.prompt_content,
    final_prompt: history.final_prompt,
    variables: history.variables,
    output: history.output,
    model: history.model,
    input_tokens: history.input_tokens,
    output_tokens: history.output_tokens,
    total_tokens: history.total_tokens,
    cost: history.cost,
    response_time: history.response_time,
    is_cached: true,
    cached_at: history.created_at
  }
  
  // 设置自动显示渲染视图
  autoShowRendered.value = true
  
  // 切换到结果标签页
  activeTab.value = 'result'
  
  // 关闭抽屉
  executionHistoryDrawerVisible.value = false
  
  ElMessage.success('已加载历史执行结果')
}

function formatDate(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  // 小于1分钟
  if (diff < 60 * 1000) {
    return '刚刚'
  }
  
  // 小于1小时
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000))
    return `${minutes} 分钟前`
  }
  
  // 小于24小时
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    return `${hours} 小时前`
  }
  
  // 小于7天
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000))
    return `${days} 天前`
  }
  
  // 格式化为标准日期时间
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
}
</script>

<style scoped>
.prompt-editor-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.editor-container {
  flex: 1;
  overflow: hidden;
  padding: 1.5rem;
}

.editor-main {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  border: 1px solid #e1e4e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.toolbar {
  background: white;
  border-bottom: 1px solid #e1e4e8;
  padding: 1rem 1.5rem;
}

.toolbar .flex {
  align-items: center;
}

.toolbar .text-gray-400 {
  color: #cbd5e0;
  margin: 0 0.75rem;
}

.toolbar .text-gray-600 {
  color: #586069;
  font-weight: 600;
  font-size: 0.95rem;
}

.editor-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.editor-left {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 2.5rem;
  background: white;
}

.editor-left::-webkit-scrollbar {
  width: 8px;
}

.editor-left::-webkit-scrollbar-track {
  background: #f6f8fa;
}

.editor-left::-webkit-scrollbar-thumb {
  background: #d1d5da;
  border-radius: 4px;
}

.editor-left::-webkit-scrollbar-thumb:hover {
  background: #959da5;
}

.editor-right {
  width: 480px;
  background: #fafbfc;
  border-left: 1px solid #e1e4e8;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.editor-right :deep(.el-tabs) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-right :deep(.el-tabs__header) {
  margin: 0;
  background: white;
  padding: 1rem 1.5rem 0;
  border-bottom: 1px solid #e1e4e8;
}

.editor-right :deep(.el-tabs__item) {
  font-weight: 500;
  font-size: 0.9rem;
  color: #586069;
}

.editor-right :deep(.el-tabs__item:hover) {
  color: #0366d6;
}

.editor-right :deep(.el-tabs__item.is-active) {
  color: #24292e;
  font-weight: 600;
}

.editor-right :deep(.el-tabs__active-bar) {
  height: 2px;
  background: #0366d6;
}

.editor-right :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.editor-right :deep(.el-tabs__content)::-webkit-scrollbar {
  width: 8px;
}

.editor-right :deep(.el-tabs__content)::-webkit-scrollbar-track {
  background: #f6f8fa;
}

.editor-right :deep(.el-tabs__content)::-webkit-scrollbar-thumb {
  background: #d1d5da;
  border-radius: 4px;
}

.form-section {
  max-width: 900px;
  margin: 0 auto;
}

.form-section :deep(.el-form-item__label) {
  font-weight: 600;
  color: #24292e;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.form-section :deep(.el-input__wrapper) {
  box-shadow: none;
  border-radius: 6px;
  transition: all 0.15s;
  background-color: #ffffff;
  border: 1px solid #d1d5da;
}

.form-section :deep(.el-input__wrapper:hover) {
  border-color: #a8adb3;
}

.form-section :deep(.el-input__wrapper.is-focus) {
  border-color: #0366d6;
  box-shadow: 0 0 0 3px rgba(3, 102, 214, 0.1);
}

.form-section :deep(.el-input__inner) {
  color: #24292e;
  font-size: 0.9rem;
}

.form-section :deep(.el-textarea__inner) {
  box-shadow: none;
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', 'SF Mono', 'Courier New', monospace;
  line-height: 1.6;
  transition: all 0.15s;
  background-color: #ffffff;
  color: #24292e;
  font-size: 14px;
  border: 1px solid #d1d5da;
  padding: 10px 12px;
}

.form-section :deep(.el-textarea__inner:hover) {
  border-color: #a8adb3;
}

.form-section :deep(.el-textarea__inner:focus) {
  border-color: #0366d6;
  box-shadow: 0 0 0 3px rgba(3, 102, 214, 0.1);
}

.form-section :deep(.el-textarea__inner::placeholder),
.form-section :deep(.el-input__inner::placeholder) {
  color: #94a3b8;
  font-weight: 400;
}

.form-section :deep(.el-select) {
  width: 100%;
}

.form-section :deep(.el-checkbox) {
  font-size: 0.95rem;
  color: #4a5568;
}

.settings-panel {
  padding: 0;
}

.settings-panel :deep(.el-form-item__label) {
  font-weight: 600;
  color: #2d3748;
}

.text-xs {
  font-size: 0.75rem;
  line-height: 1rem;
}

.text-gray-500 {
  color: #6b7280;
}

.mt-1 {
  margin-top: 0.25rem;
}

/* 按钮优化 */
:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.15s;
}

:deep(.el-button--primary) {
  background: #0366d6;
  border-color: #0366d6;
}

:deep(.el-button--primary:hover) {
  background: #0256c5;
  border-color: #0256c5;
}

:deep(.el-button--success) {
  background: #28a745;
  border-color: #28a745;
}

:deep(.el-button--success:hover) {
  background: #22863a;
  border-color: #22863a;
}

:deep(.el-button--danger) {
  background: #d73a49;
  border-color: #d73a49;
}

:deep(.el-button--danger:hover) {
  background: #cb2431;
  border-color: #cb2431;
}

/* 版本历史样式 */
.version-history-container {
  padding: 1rem;
  background: #fafbfc;
}

.version-card {
  margin-bottom: 1rem;
  border-radius: 6px;
  transition: all 0.15s;
  border: 1px solid #e1e4e8;
  background: white;
}

.version-card:hover {
  box-shadow: 0 1px 5px rgba(27, 31, 35, 0.1);
  border-color: #d1d5da;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e1e4e8;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.version-number {
  font-weight: 600;
  font-size: 1rem;
  color: #0366d6;
}

.version-actions {
  display: flex;
  gap: 0.5rem;
}

.version-summary {
  padding: 0.5rem 0;
}

.version-title {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.version-change {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: #f1f5f9;
  border-radius: 4px;
  border-left: 3px solid #3b82f6;
}

.version-meta {
  color: #94a3b8;
  font-size: 0.85rem;
}

.version-content-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.version-meta-info {
  margin-bottom: 1.5rem;
}

.version-content-preview {
  margin-top: 1.5rem;
}

.version-content-preview h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.content-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.content-box pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #334155;
}

:deep(.el-timeline) {
  padding-left: 0;
}

:deep(.el-timeline-item__timestamp) {
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 500;
}

:deep(.el-drawer__header) {
  margin-bottom: 1.5rem;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 2px solid #e2e8f0;
}

:deep(.el-drawer__title) {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

:deep(.el-drawer__body) {
  padding: 0;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #475569;
}

:deep(.el-descriptions__content) {
  color: #1e293b;
}

/* 执行历史样式 */
.execution-history-container {
  padding: 1rem;
  background: #fafbfc;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-card {
  border-radius: 6px;
  transition: all 0.15s;
  border: 1px solid #e1e4e8;
  background: white;
}

.history-card:hover {
  box-shadow: 0 1px 5px rgba(27, 31, 35, 0.1);
  border-color: #d1d5da;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e1e4e8;
}

.history-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #586069;
  font-size: 0.85rem;
  font-weight: 500;
}

.history-time .el-icon {
  font-size: 1rem;
  color: #0366d6;
}

.history-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.info-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.info-row .label {
  color: #586069;
  font-weight: 500;
}

.info-row .value {
  color: #24292e;
  font-weight: 600;
}
</style>

