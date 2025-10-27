<template>
  <div class="global-ai-config-page">
    <Header />
    
    <div class="content-wrapper">
      <div class="page-container">
        <!-- 页面标题 -->
        <div class="page-header">
          <div>
            <h1 class="page-title">
              <el-icon><Connection /></el-icon>
              全局AI配置
            </h1>
            <p class="page-description">
              配置系统默认的AI服务，让用户无需配置即可使用
            </p>
          </div>
          <div class="header-actions">
            <el-button @click="loadConfig" :icon="Refresh">刷新</el-button>
            <el-button 
              type="success" 
              @click="testConfig" 
              :loading="testing"
              :icon="CircleCheck"
              :disabled="!config.enable_default_ai"
            >
              测试连接
            </el-button>
            <el-button 
              type="primary" 
              @click="saveConfig" 
              :loading="saving"
              :icon="Check"
            >
              保存配置
            </el-button>
          </div>
        </div>

        <!-- 配置表单 -->
        <el-card shadow="never" class="config-card">
          <el-form 
            ref="formRef" 
            :model="config" 
            label-width="140px"
            label-position="left"
          >
            <!-- 启用开关 -->
            <el-form-item>
              <template #label>
                <span class="form-label">
                  <el-icon><Switch /></el-icon>
                  启用全局AI
                </span>
              </template>
              <div class="switch-container">
                <el-switch 
                  v-model="config.enable_default_ai"
                  size="large"
                  active-text="已启用"
                  inactive-text="已禁用"
                />
                <span class="switch-hint">
                  启用后，未配置AI的用户将使用此全局配置
                </span>
              </div>
            </el-form-item>

            <el-divider />

            <!-- AI模型 -->
            <el-form-item label="AI模型">
              <el-input
                v-model="config.default_ai_model"
                placeholder="例如: gpt-3.5-turbo"
                :disabled="!config.enable_default_ai"
              />
            </el-form-item>

            <!-- Base URL -->
            <el-form-item label="Base URL">
              <el-input
                v-model="config.default_ai_base_url"
                placeholder="例如: https://api.openai.com/v1"
                :disabled="!config.enable_default_ai"
              />
            </el-form-item>

            <!-- API Key -->
            <el-form-item>
              <template #label>
                <span class="form-label">
                  <el-icon><Key /></el-icon>
                  API Key
                </span>
              </template>
              <div class="api-key-container">
                <el-input
                  v-model="config.default_ai_api_key"
                  :type="showApiKey ? 'text' : 'password'"
                  placeholder="请输入API Key"
                  :disabled="!config.enable_default_ai"
                  show-password
                >
                  <template #append>
                    <el-button 
                      :icon="showApiKey ? View : Hide"
                      @click="showApiKey = !showApiKey"
                    />
                  </template>
                </el-input>
                <div v-if="originalConfig.has_api_key && !apiKeyChanged" class="api-key-hint">
                  <el-icon color="#67c23a"><CircleCheck /></el-icon>
                  已配置API Key（修改后将覆盖原有配置）
                </div>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Connection, Refresh, Check, CircleCheck, Switch, Key, 
  View, Hide
} from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import { systemAPI } from '@/api'

interface GlobalAIConfig {
  id?: number | null
  enable_default_ai: boolean
  default_ai_model: string
  default_ai_api_key: string | null
  default_ai_base_url: string
  has_api_key?: boolean
  name?: string
  description?: string
}

const config = reactive<GlobalAIConfig>({
  enable_default_ai: false,
  default_ai_model: 'gpt-3.5-turbo',
  default_ai_api_key: '',
  default_ai_base_url: 'https://api.openai.com/v1'
})

const originalConfig = ref<GlobalAIConfig>({
  enable_default_ai: false,
  default_ai_model: 'gpt-3.5-turbo',
  default_ai_api_key: '',
  default_ai_base_url: 'https://api.openai.com/v1',
  has_api_key: false
})

const saving = ref(false)
const testing = ref(false)
const showApiKey = ref(false)

const apiKeyChanged = computed(() => {
  return config.default_ai_api_key !== originalConfig.value.default_ai_api_key
})

// 加载配置
const loadConfig = async () => {
  try {
    const response = await systemAPI.getGlobalAIConfig()
    // 响应拦截器返回的格式是 { data: ..., message: ... }
    const data = response.data
    
    Object.assign(config, data)
    originalConfig.value = { ...data }
    
    console.log('[DEBUG] GlobalAIConfig 加载的配置:', config)
    ElMessage.success('配置加载成功')
  } catch (error: any) {
    console.error('[ERROR] 加载配置失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载配置失败')
  }
}

// 保存配置
const saveConfig = async () => {
  // 验证
  if (config.enable_default_ai) {
    if (!config.default_ai_model) {
      ElMessage.warning('请输入AI模型')
      return
    }
    if (!config.default_ai_base_url) {
      ElMessage.warning('请输入Base URL')
      return
    }
    if (!config.default_ai_api_key && !originalConfig.value.has_api_key) {
      ElMessage.warning('请输入API Key')
      return
    }
  }

  saving.value = true
  try {
    const updateData: any = {
      enable_default_ai: config.enable_default_ai,
      default_ai_model: config.default_ai_model,
      default_ai_base_url: config.default_ai_base_url
    }

    // 只在修改了API Key时才发送
    if (apiKeyChanged.value && config.default_ai_api_key) {
      updateData.default_ai_api_key = config.default_ai_api_key
    }

    await systemAPI.updateGlobalAIConfig(updateData)
    
    ElMessage.success('全局AI配置保存成功')
    await loadConfig()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存配置失败')
  } finally {
    saving.value = false
  }
}

// 测试配置
const testConfig = async () => {
  if (!config.enable_default_ai) {
    ElMessage.warning('请先启用全局AI')
    return
  }

  testing.value = true
  try {
    await systemAPI.testGlobalAIConfig()
    // 响应拦截器返回的格式是 { data: ..., message: ... }
    
    ElMessage.success('全局AI配置测试成功，连接正常')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '测试失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.global-ai-config-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
}

.page-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-description {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.config-card {
  margin-bottom: 24px;
}

.config-card :deep(.el-card__body) {
  padding: 32px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.switch-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.switch-hint {
  font-size: 13px;
  color: #909399;
}

.provider-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.provider-desc {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.api-key-container {
  width: 100%;
}

.api-key-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #67c23a;
  display: flex;
  align-items: center;
  gap: 6px;
}

</style>

