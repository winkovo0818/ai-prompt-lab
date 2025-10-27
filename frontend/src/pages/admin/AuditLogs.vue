<template>
  <div class="audit-logs-container">
    <Header />
    
    <div class="audit-logs-page">
      <div class="page-header">
      <div class="header-content">
        <h1>
          <el-icon><Document /></el-icon>
          审计日志
        </h1>
        <p class="subtitle">查看系统操作记录和安全事件</p>
      </div>
      
      <div class="header-actions">
        <el-button @click="router.push('/admin/security-config')" :icon="Lock">安全配置</el-button>
        <el-button @click="loadStats" :icon="Refresh">刷新</el-button>
        <el-button type="primary" @click="exportLogs" :icon="Download">导出日志</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="stats">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><Operation /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total_operations }}</div>
          <div class="stat-label">总操作数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon failed">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.failed_operations }}</div>
          <div class="stat-label">失败操作</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon high-risk">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.high_risk_operations }}</div>
          <div class="stat-label">高风险操作</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon sensitive">
          <el-icon><Lock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.sensitive_operations }}</div>
          <div class="stat-label">敏感操作</div>
        </div>
      </div>
    </div>

    <!-- 筛选器 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="操作类型">
          <el-input v-model="filters.action" placeholder="如 user_login" clearable />
        </el-form-item>
        
        <el-form-item label="资源类型">
          <el-select v-model="filters.resource" placeholder="选择资源" clearable>
            <el-option label="用户" value="user" />
            <el-option label="Prompt" value="prompt" />
            <el-option label="API密钥" value="api_key" />
            <el-option label="安全配置" value="security_config" />
            <el-option label="安全" value="security" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failure" />
            <el-option label="警告" value="warning" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="风险等级">
          <el-select v-model="filters.risk_level" placeholder="选择风险" clearable>
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="严重" value="critical" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadLogs" :icon="Search">查询</el-button>
          <el-button @click="resetFilters" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 日志表格 -->
    <el-card class="table-card">
      <el-table 
        :data="logs" 
        v-loading="loading"
        stripe
        style="width: 100%"
        @row-click="viewDetail"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="用户" width="150">
          <template #default="{ row }">
            <div v-if="row.username">
              <el-icon><User /></el-icon>
              {{ row.username }}
            </div>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-tag size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="资源" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.resource }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="描述" min-width="300">
          <template #default="{ row }">
            {{ row.description }}
          </template>
        </el-table-column>
        
        <el-table-column label="IP地址" width="150">
          <template #default="{ row }">
            {{ row.ip_address || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="getStatusType(row.status)" 
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="风险" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="getRiskType(row.risk_level)" 
              size="small"
              effect="dark"
            >
              {{ getRiskText(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="敏感" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.is_sensitive" color="#f56c6c"><Lock /></el-icon>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadLogs"
          @current-change="loadLogs"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="日志详情"
      width="800px"
    >
      <div v-if="selectedLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedLog.id }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ formatDate(selectedLog.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="用户">{{ selectedLog.username || '-' }}</el-descriptions-item>
          <el-descriptions-item label="用户ID">{{ selectedLog.user_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="操作">{{ selectedLog.action }}</el-descriptions-item>
          <el-descriptions-item label="资源">{{ selectedLog.resource }}</el-descriptions-item>
          <el-descriptions-item label="资源ID">{{ selectedLog.resource_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedLog.status)">
              {{ getStatusText(selectedLog.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskType(selectedLog.risk_level)" effect="dark">
              {{ getRiskText(selectedLog.risk_level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="敏感操作">
            {{ selectedLog.is_sensitive ? '是' : '否' }}
          </el-descriptions-item>
          <el-descriptions-item label="IP地址">{{ selectedLog.ip_address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="请求方法">{{ selectedLog.request_method || '-' }}</el-descriptions-item>
          <el-descriptions-item label="请求路径" :span="2">{{ selectedLog.request_path || '-' }}</el-descriptions-item>
          <el-descriptions-item label="User-Agent" :span="2">
            <div style="max-width: 600px; word-break: break-all;">
              {{ selectedLog.user_agent || '-' }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedLog.description }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedLog.error_message" label="错误信息" :span="2">
            <el-alert type="error" :closable="false">
              {{ selectedLog.error_message }}
            </el-alert>
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedLog.details" class="detail-json">
          <h4>详细信息</h4>
          <pre>{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Document, Refresh, Download, Search, RefreshLeft, 
  Operation, WarningFilled, Warning, Lock, User 
} from '@element-plus/icons-vue'
import request from '@/api/request'
import Header from '@/components/Layout/Header.vue'

const router = useRouter()

const loading = ref(false)
const logs = ref<any[]>([])
const stats = ref<any>(null)
const detailVisible = ref(false)
const selectedLog = ref<any>(null)
const dateRange = ref<string[]>([])

const filters = reactive({
  action: '',
  resource: '',
  status: '',
  risk_level: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

onMounted(() => {
  loadLogs()
  loadStats()
})

async function loadLogs() {
  loading.value = true
  try {
    const params: any = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    
    if (filters.action) params.action = filters.action
    if (filters.resource) params.resource = filters.resource
    if (filters.status) params.status = filters.status
    if (filters.risk_level) params.risk_level = filters.risk_level
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await request.get('/api/security/audit-logs', { params })
    logs.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '加载日志失败')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const response = await request.get('/api/security/audit-logs/stats', {
      params: { days: 7 }
    })
    stats.value = response.data
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

function resetFilters() {
  filters.action = ''
  filters.resource = ''
  filters.status = ''
  filters.risk_level = ''
  dateRange.value = []
  pagination.page = 1
  loadLogs()
}

function viewDetail(row: any) {
  selectedLog.value = row
  detailVisible.value = true
}

function exportLogs() {
  ElMessage.info('导出功能开发中...')
}

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

function getStatusType(status: string) {
  const types: Record<string, any> = {
    success: 'success',
    failure: 'danger',
    warning: 'warning'
  }
  return types[status] || 'info'
}

function getStatusText(status: string) {
  const texts: Record<string, string> = {
    success: '成功',
    failure: '失败',
    warning: '警告'
  }
  return texts[status] || status
}

function getRiskType(level: string) {
  const types: Record<string, any> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return types[level] || 'info'
}

function getRiskText(level: string) {
  const texts: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '严重'
  }
  return texts[level] || level
}
</script>

<style scoped>
.audit-logs-container {
  background: #f5f7fa;
}

.audit-logs-page {
  padding: 24px;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content h1 {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.header-content h1 .el-icon {
  font-size: 32px;
  color: #409eff;
}

.subtitle {
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.failed {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.high-risk {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
}

.stat-icon.sensitive {
  background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.filter-card {
  margin-bottom: 16px;
}

.filter-form {
  margin: 0;
}

.table-card {
  background: white;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.log-detail {
  padding: 16px 0;
}

.detail-json {
  margin-top: 24px;
}

.detail-json h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
}

.detail-json pre {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
}

.text-gray {
  color: #c0c4cc;
}
</style>

