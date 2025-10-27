<template>
  <div class="settings-page">
    <Header />
    
    <div class="content-container">
      <div class="main-content p-6">
        <div class="page-header mb-6">
          <h1 class="text-2xl font-bold text-gray-900 mb-2">AI 配置管理</h1>
          <p class="text-gray-600">配置多个 AI 以便在测试中使用</p>
        </div>

        <div class="settings-content">
          <!-- 全局AI配置（仅管理员可见） -->
          <div v-if="userStore.userInfo?.role === 'admin'" class="global-ai-section">
            <div class="section-header">
              <div>
                <h2 class="text-lg font-semibold text-gray-900">全局AI配置</h2>
                <p class="text-sm text-gray-500 mt-1">为未配置AI的用户提供默认服务</p>
              </div>
              <el-button @click="navigateToGlobalConfig" :icon="Setting">
                管理全局配置
              </el-button>
            </div>
            
            <el-card v-if="globalAIConfig" shadow="never" class="global-config-card">
              <div class="global-config-info">
                <div class="config-status">
                  <el-tag :type="globalAIConfig.enable_default_ai ? 'success' : 'info'" size="large">
                    {{ globalAIConfig.enable_default_ai ? '已启用' : '未启用' }}
                  </el-tag>
                </div>
                <div v-if="globalAIConfig.enable_default_ai" class="config-details">
                  <div class="detail-item">
                    <span class="label">模型:</span>
                    <span class="value">{{ globalAIConfig.default_ai_model }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Base URL:</span>
                    <span class="value">{{ globalAIConfig.default_ai_base_url }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">API Key:</span>
                    <span class="value">{{ globalAIConfig.default_ai_api_key || '已配置' }}</span>
                  </div>
                </div>
                <div v-else class="config-hint">
                  <el-icon><InfoFilled /></el-icon>
                  <span>未启用全局AI，用户需要自行配置</span>
                </div>
              </div>
            </el-card>
          </div>

          <!-- AI 配置列表 -->
          <div class="ai-configs-section">
            <div class="section-header">
              <h2 class="text-lg font-semibold text-gray-900">我的 AI 配置</h2>
              <el-button type="primary" @click="showAddDialog = true">
                <el-icon><Plus /></el-icon>
                添加 AI 配置
              </el-button>
            </div>

            <div v-if="userOwnedConfigs.length === 0" class="empty-state">
              <el-empty description="还没有配置 AI">
                <el-button type="primary" @click="showAddDialog = true">
                  <el-icon><Plus /></el-icon>
                  添加第一个 AI
                </el-button>
              </el-empty>
            </div>

            <div v-else class="ai-configs-list">
              <div 
                v-for="config in userOwnedConfigs" 
                :key="config.id"
                class="ai-config-card"
              >
                <div class="card-header">
                  <div class="card-title">
                    <el-icon><Cpu /></el-icon>
                    <h3>{{ config.name }}</h3>
                  </div>
                  <div class="card-actions">
                    <el-button link @click="handleEdit(config)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button link type="danger" @click="handleDelete(config.id)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
                <div class="card-content">
                  <div class="config-item">
                    <span class="label">Base URL:</span>
                    <span class="value">{{ config.baseUrl }}</span>
                  </div>
                  <div class="config-item">
                    <span class="label">模型:</span>
                    <span class="value">{{ config.model }}</span>
                  </div>
                  <div class="config-item">
                    <span class="label">API Key:</span>
                    <span class="value">{{ maskApiKey(config.apiKey) }}</span>
                  </div>
                  <div v-if="config.description" class="config-item">
                    <span class="label">描述:</span>
                    <span class="value">{{ config.description }}</span>
                  </div>
                </div>
                <div class="card-footer">
                  <el-button 
                    type="primary" 
                    plain 
                    size="small"
                    :loading="testingConfigId === config.id"
                    @click="handleTestConnection(config.id)"
                  >
                    <el-icon><Connection /></el-icon>
                    测试连接
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 默认参数配置 -->
          <div class="default-params-section">
            <div class="section-header">
              <h2 class="text-lg font-semibold text-gray-900">默认参数</h2>
            </div>
            <el-form label-position="top">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="Temperature">
                    <div class="slider-value">{{ configStore.temperature }}</div>
                    <el-slider
                      v-model="configStore.temperature"
                      :min="0"
                      :max="2"
                      :step="0.1"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Max Tokens">
                    <div class="slider-value">{{ configStore.maxTokens }}</div>
                    <el-slider
                      v-model="configStore.maxTokens"
                      :min="100"
                      :max="4000"
                      :step="100"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item>
                <el-button type="primary" @click="saveDefaultParams">
                  <el-icon><Check /></el-icon>
                  保存默认参数
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑 AI 配置对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingConfig ? '编辑 AI 配置' : '添加 AI 配置'"
      width="600px"
    >
      <el-form :model="formData" label-position="top">
        <el-form-item label="配置名称" required>
          <el-input
            v-model="formData.name"
            placeholder="例如：OpenAI GPT-4"
          />
        </el-form-item>

        <el-form-item label="API Base URL" required>
          <el-input
            v-model="formData.baseUrl"
            placeholder="https://api.openai.com/v1"
          />
        </el-form-item>

        <el-form-item label="API Key" required>
          <el-input
            v-model="formData.apiKey"
            type="password"
            placeholder="sk-..."
            show-password
          />
        </el-form-item>

        <el-form-item label="默认模型" required>
          <el-select 
            v-model="formData.model"
            filterable
            allow-create
            placeholder="选择或输入模型 ID"
          >
            <el-option
              v-for="model in configStore.availableModels"
              :key="model.id"
              :label="model.name"
              :value="model.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="简单描述这个 AI 配置"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <div class="left-actions">
            <el-button 
              plain
              :loading="testing"
              @click="handleTestInDialog"
            >
              <el-icon><Connection /></el-icon>
              测试连接
            </el-button>
          </div>
          <div class="right-actions">
            <el-button @click="showAddDialog = false">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">
              {{ editingConfig ? '保存' : '添加' }}
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '@/store/config'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Cpu, Check, Connection, Setting, InfoFilled } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import type { AIConfig } from '@/store/config'
import { aiConfigAPI, systemAPI } from '@/api'

const router = useRouter()
const configStore = useConfigStore()
const userStore = useUserStore()

// 全局AI配置
const globalAIConfig = ref<any>(null)

const showAddDialog = ref(false)
const editingConfig = ref<AIConfig | null>(null)
const saving = ref(false)
const loading = ref(false)
const testing = ref(false)
const testingConfigId = ref<number | null>(null)

// 过滤出用户自己的配置（排除全局配置）
const userOwnedConfigs = computed(() => {
  return configStore.aiConfigs.filter(config => !config.isGlobal)
})

const formData = reactive({
  name: '',
  baseUrl: 'https://api.openai.com/v1',
  apiKey: '',
  model: 'gpt-3.5-turbo',
  description: ''
})

onMounted(async () => {
  loading.value = true
  try {
    await configStore.loadAIConfigs()
    
    // 如果是管理员，加载全局AI配置
    if (userStore.userInfo?.role === 'admin') {
      await loadGlobalAIConfig()
    }
  } finally {
    loading.value = false
  }
})

// 加载全局AI配置
async function loadGlobalAIConfig() {
  try {
    const response = await systemAPI.getGlobalAIConfig()
    // 响应拦截器返回的格式是 { data: ..., message: ... }
    globalAIConfig.value = response.data
    console.log('[DEBUG] 加载的全局AI配置:', globalAIConfig.value)
  } catch (error) {
    console.error('加载全局AI配置失败:', error)
  }
}

// 导航到全局配置页面
function navigateToGlobalConfig() {
  router.push('/admin/global-ai-config')
}

function maskApiKey(apiKey: string): string {
  if (!apiKey) return ''
  if (apiKey.length <= 8) return '***'
  return apiKey.substring(0, 7) + '...' + apiKey.substring(apiKey.length - 4)
}

function handleEdit(config: AIConfig) {
  editingConfig.value = config
  formData.name = config.name
  formData.baseUrl = config.baseUrl
  formData.apiKey = config.apiKey
  formData.model = config.model
  formData.description = config.description || ''
  showAddDialog.value = true
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这个 AI 配置吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await configStore.deleteAIConfig(id)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

async function handleSave() {
  if (!formData.name || !formData.baseUrl || !formData.apiKey || !formData.model) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  saving.value = true
  try {
    if (editingConfig.value) {
      // 更新
      await configStore.updateAIConfig(editingConfig.value.id, {
        name: formData.name,
        baseUrl: formData.baseUrl,
        apiKey: formData.apiKey,
        model: formData.model,
        description: formData.description
      })
      ElMessage.success('更新成功')
    } else {
      // 新增
      await configStore.addAIConfig({
        name: formData.name,
        baseUrl: formData.baseUrl,
        apiKey: formData.apiKey,
        model: formData.model,
        description: formData.description
      })
      ElMessage.success('添加成功')
    }

    showAddDialog.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

function resetForm() {
  editingConfig.value = null
  formData.name = ''
  formData.baseUrl = 'https://api.openai.com/v1'
  formData.apiKey = ''
  formData.model = 'gpt-3.5-turbo'
  formData.description = ''
}

function saveDefaultParams() {
  configStore.saveDefaultParams()
  ElMessage.success('保存成功')
}

async function handleTestConnection(configId: number) {
  testingConfigId.value = configId
  
  try {
    const response = await aiConfigAPI.test(configId) as any
    
    // axios 拦截器已经处理了 code === 0 的判断
    // 如果到达这里，说明测试成功
    ElMessage.success({
      message: response.message || '连接测试成功',
      duration: 3000
    })
  } catch (error: any) {
    // axios 拦截器已经显示了错误消息
    // 这里只需要记录日志
    console.error('测试连接失败:', error)
  } finally {
    testingConfigId.value = null
  }
}

async function handleTestInDialog() {
  // 验证必填字段
  if (!formData.name || !formData.baseUrl || !formData.apiKey || !formData.model) {
    ElMessage.warning('请先填写所有必填项（配置名称、Base URL、API Key、模型）')
    return
  }

  testing.value = true
  
  try {
    const response = await aiConfigAPI.testConnection({
      name: formData.name,
      base_url: formData.baseUrl,
      api_key: formData.apiKey,
      model: formData.model,
      description: formData.description
    }) as any
    
    // axios 拦截器已经处理了 code === 0 的判断
    // 如果到达这里，说明测试成功
    ElMessage.success({
      message: response.message || '连接测试成功！配置正确，可以保存',
      duration: 3000
    })
  } catch (error: any) {
    // axios 拦截器已经显示了错误消息
    // 这里只需要记录日志
    console.error('测试连接失败:', error)
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.settings-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.content-container {
  flex: 1;
  overflow: hidden;
}

.main-content {
  height: 100%;
  overflow-y: auto;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.main-content::-webkit-scrollbar {
  width: 10px;
}

.main-content::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.main-content::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 5px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.page-header {
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding-bottom: 2rem;
}

.global-ai-section,
.ai-configs-section,
.default-params-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}

.global-ai-section {
  margin-bottom: 1.5rem;
}

.global-config-card {
  margin-top: 1rem;
  border: 1px solid #e5e7eb;
}

.global-config-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.config-status {
  display: flex;
  align-items: center;
}

.config-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 6px;
}

.detail-item {
  display: flex;
  gap: 0.5rem;
}

.detail-item .label {
  font-weight: 500;
  color: #6b7280;
  min-width: 80px;
  font-size: 0.875rem;
}

.detail-item .value {
  color: #1f2937;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.875rem;
}

.config-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f3f4f6;
  border-radius: 6px;
  color: #6b7280;
  font-size: 0.875rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.empty-state {
  padding: 3rem;
  text-align: center;
}

.ai-configs-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.25rem;
}

.ai-config-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.25rem;
  transition: all 0.2s;
  background: white;
}

.ai-config-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-title .el-icon {
  font-size: 1.25rem;
  color: #3b82f6;
}

.card-title h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.card-footer {
  padding-top: 0.75rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
}

.config-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.25rem 0;
}

.config-item .label {
  font-weight: 500;
  color: #6b7280;
  min-width: 90px;
  font-size: 0.875rem;
}

.config-item .value {
  color: #1f2937;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.875rem;
  word-break: break-all;
  flex: 1;
}

.slider-value {
  font-size: 1rem;
  font-weight: 600;
  color: #3b82f6;
  text-align: center;
  margin-bottom: 0.5rem;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #6b7280;
}

:deep(.el-select) {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.left-actions {
  display: flex;
  gap: 0.5rem;
}

.right-actions {
  display: flex;
  gap: 0.5rem;
}

/* 响应式 */
@media (max-width: 768px) {
  .ai-configs-list {
    grid-template-columns: 1fr;
  }
}
</style>

