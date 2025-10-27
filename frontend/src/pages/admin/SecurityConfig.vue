<template>
  <div class="security-config-container">
    <Header />
    
    <div class="security-config-page">
      <div class="page-header">
        <div class="header-content">
          <h1>
            <el-icon><Lock /></el-icon>
            安全配置
          </h1>
          <p class="subtitle">管理系统安全策略和敏感词库</p>
        </div>
        
        <div class="header-actions">
          <el-button @click="router.push('/admin/audit-logs')" :icon="Document">查看审计日志</el-button>
          <el-button @click="loadConfig" :icon="Refresh">刷新</el-button>
          <el-button type="primary" @click="saveConfig" :loading="saving" :icon="Check">保存配置</el-button>
        </div>
      </div>

      <el-row :gutter="24" class="config-section">
        <!-- 访问控制 -->
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>访问控制</span>
            </div>
          </template>
          
          <el-form :model="config" label-width="120px" label-position="left">
            <el-form-item label="IP白名单">
              <el-switch v-model="config.ip_whitelist_enabled" />
            </el-form-item>
            
            <el-form-item v-if="config.ip_whitelist_enabled" label="白名单IP">
              <div style="width: 100%;">
                <el-tag
                  v-for="ip in config.ip_whitelist"
                  :key="ip"
                  closable
                  @close="removeIP(ip)"
                  style="margin-right: 8px; margin-bottom: 8px;"
                >
                  {{ ip }}
                </el-tag>
                <el-input
                  v-model="newIP"
                  placeholder="输入IP地址后回车"
                  @keyup.enter="addIP"
                  style="width: 100%; max-width: 300px; margin-top: 8px;"
                >
                  <template #append>
                    <el-button @click="addIP">添加</el-button>
                  </template>
                </el-input>
              </div>
            </el-form-item>
            
            <el-form-item label="频率限制">
              <el-switch v-model="config.rate_limit_enabled" />
            </el-form-item>
            
            <el-form-item v-if="config.rate_limit_enabled" label="每分钟请求">
              <el-input-number v-model="config.max_requests_per_minute" :min="1" :max="1000" />
            </el-form-item>
            
            <el-form-item v-if="config.rate_limit_enabled" label="每小时请求">
              <el-input-number v-model="config.max_requests_per_hour" :min="1" :max="100000" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

        <!-- 内容审核 -->
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="config-card">
            <template #header>
              <div class="card-header">
                <el-icon><View /></el-icon>
                <span>内容审核</span>
              </div>
            </template>
            
            <el-form :model="config" label-width="120px" label-position="left">
              <el-form-item label="启用内容审核">
                <el-switch v-model="config.content_audit_enabled" />
              </el-form-item>
              
              <el-form-item label="自动脱敏">
                <el-switch v-model="config.auto_mask_sensitive_info" />
              </el-form-item>
              
              <el-form-item label="拦截敏感词">
                <el-switch v-model="config.block_sensitive_words" />
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="24" class="config-section">
        <!-- 密钥安全 -->
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="config-card">
            <template #header>
              <div class="card-header">
                <el-icon><Key /></el-icon>
                <span>密钥安全</span>
              </div>
            </template>
            
            <el-form :model="config" label-width="140px" label-position="left">
              <el-form-item label="加密存储">
                <el-switch v-model="config.api_key_encryption_enabled" />
              </el-form-item>
              
              <el-form-item label="会话超时(分钟)">
                <el-input-number v-model="config.session_timeout_minutes" :min="5" :max="1440" />
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 审计日志配置 -->
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="config-card">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>审计日志</span>
              </div>
            </template>
            
            <el-form :model="config" label-width="140px" label-position="left">
              <el-form-item label="日志保留天数">
                <div class="form-item-content">
                  <el-input-number v-model="config.audit_log_retention_days" :min="1" :max="365" />
                  <span class="form-hint">过期日志将被自动清理</span>
                </div>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- 敏感词管理 -->
      <el-row :gutter="24" class="config-section">
        <el-col :span="24">
          <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><WarningFilled /></el-icon>
              <span>敏感词管理</span>
              <el-button 
                type="primary" 
                size="small" 
                @click="showAddWordDialog"
                style="margin-left: auto;"
              >
                添加敏感词
              </el-button>
            </div>
          </template>
          
          <el-tabs v-model="activeTab">
            <el-tab-pane label="全部" name="all">
              <sensitive-words-table :category="null" @refresh="loadSensitiveWords" />
            </el-tab-pane>
            <el-tab-pane label="暴力色情" name="nsfw">
              <sensitive-words-table category="nsfw" @refresh="loadSensitiveWords" />
            </el-tab-pane>
            <el-tab-pane label="违法内容" name="illegal">
              <sensitive-words-table category="illegal" @refresh="loadSensitiveWords" />
            </el-tab-pane>
            <el-tab-pane label="欺诈诈骗" name="fraud">
              <sensitive-words-table category="fraud" @refresh="loadSensitiveWords" />
            </el-tab-pane>
            <el-tab-pane label="自定义" name="custom">
              <sensitive-words-table category="custom" @refresh="loadSensitiveWords" />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加敏感词对话框 -->
    <el-dialog
      v-model="addWordVisible"
      title="添加敏感词"
      width="500px"
    >
      <el-form :model="newWord" label-width="100px">
        <el-form-item label="敏感词" required>
          <el-input v-model="newWord.word" placeholder="输入敏感词" />
        </el-form-item>
        
        <el-form-item label="分类" required>
          <el-select v-model="newWord.category" placeholder="选择分类">
            <el-option label="暴力色情" value="nsfw" />
            <el-option label="违法内容" value="illegal" />
            <el-option label="欺诈诈骗" value="fraud" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="严重程度">
          <el-slider v-model="newWord.severity" :min="0" :max="100" show-input />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="addWordVisible = false">取消</el-button>
        <el-button type="primary" @click="addSensitiveWord" :loading="adding">添加</el-button>
      </template>
    </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Lock, Refresh, Check, Connection, View, Key, 
  Document, WarningFilled 
} from '@element-plus/icons-vue'
import request from '@/api/request'
import SensitiveWordsTable from './components/SensitiveWordsTable.vue'
import Header from '@/components/Layout/Header.vue'

const router = useRouter()

const saving = ref(false)
const adding = ref(false)
const activeTab = ref('all')
const addWordVisible = ref(false)
const newIP = ref('')

const config = reactive({
  ip_whitelist: [] as string[],
  ip_whitelist_enabled: false,
  rate_limit_enabled: true,
  max_requests_per_minute: 60,
  max_requests_per_hour: 1000,
  content_audit_enabled: true,
  auto_mask_sensitive_info: true,
  block_sensitive_words: true,
  api_key_encryption_enabled: true,
  session_timeout_minutes: 480,
  audit_log_retention_days: 90
})

const newWord = reactive({
  word: '',
  category: 'custom',
  severity: 50
})

onMounted(() => {
  loadConfig()
})

async function loadConfig() {
  try {
    const response = await request.get('/api/security/config')
    Object.assign(config, response.data)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '加载配置失败')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    await request.put('/api/security/config', config)
    ElMessage.success('配置已保存')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function addIP() {
  if (!newIP.value) return
  
  // 简单的IP格式验证
  const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/
  if (!ipPattern.test(newIP.value)) {
    ElMessage.warning('请输入有效的IP地址')
    return
  }
  
  if (!config.ip_whitelist) {
    config.ip_whitelist = []
  }
  
  if (config.ip_whitelist.includes(newIP.value)) {
    ElMessage.warning('该IP已存在')
    return
  }
  
  config.ip_whitelist.push(newIP.value)
  newIP.value = ''
}

function removeIP(ip: string) {
  const index = config.ip_whitelist.indexOf(ip)
  if (index > -1) {
    config.ip_whitelist.splice(index, 1)
  }
}

function showAddWordDialog() {
  newWord.word = ''
  newWord.category = 'custom'
  newWord.severity = 50
  addWordVisible.value = true
}

async function addSensitiveWord() {
  if (!newWord.word) {
    ElMessage.warning('请输入敏感词')
    return
  }
  
  adding.value = true
  try {
    await request.post('/api/security/sensitive-words', newWord)
    ElMessage.success('敏感词已添加')
    addWordVisible.value = false
    loadSensitiveWords()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '添加失败')
  } finally {
    adding.value = false
  }
}

function loadSensitiveWords() {
  // 触发子组件刷新
}
</script>

<style scoped>
.security-config-container {
  background: #f5f7fa;
}

.security-config-page {
  padding: 20px;
  background: #f5f7fa;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.header-content h1 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.header-content h1 .el-icon {
  font-size: 24px;
  color: #409eff;
}

.subtitle {
  color: #909399;
  margin: 0;
  font-size: 13px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.config-section {
  margin-bottom: 16px;
}

.config-card {
  height: 100%;
}

.config-card :deep(.el-card__header) {
  padding: 12px 16px;
  background: #fafafa;
}

.config-card :deep(.el-card__body) {
  padding: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
}

.card-header .el-icon {
  font-size: 16px;
}

.card-header span {
  flex: 1;
}

.form-item-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.form-hint {
  font-size: 12px;
  color: #909399;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}
</style>

