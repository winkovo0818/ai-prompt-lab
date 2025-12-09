<template>
  <div class="quota-manage-page">
    <Header />
    
    <div class="page-container">
      <div class="page-header">
        <h1>
          <el-icon><Odometer /></el-icon>
          API 配额管理
        </h1>
        <p>管理用户和团队的 API 调用限额</p>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon requests">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalStats.totalRequests.toLocaleString() }}</span>
            <span class="stat-label">近7天总请求</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon tokens">
            <el-icon><Coin /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ formatNumber(totalStats.totalTokens) }}</span>
            <span class="stat-label">近7天 Token</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon cost">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">${{ totalStats.totalCost.toFixed(2) }}</span>
            <span class="stat-label">近7天费用</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon users">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalStats.activeUsers }}</span>
            <span class="stat-label">活跃用户</span>
          </div>
        </div>
      </div>

      <!-- 标签页 -->
      <el-tabs v-model="activeTab" class="quota-tabs">
        <!-- 用户使用量 -->
        <el-tab-pane label="用户使用量" name="usage">
          <div class="tab-content">
            <el-table :data="usageList" v-loading="loadingUsage" stripe>
              <el-table-column prop="username" label="用户" width="150" />
              <el-table-column prop="total_requests" label="请求数" width="120">
                <template #default="{ row }">
                  {{ row.total_requests.toLocaleString() }}
                </template>
              </el-table-column>
              <el-table-column prop="total_tokens" label="Token 数" width="150">
                <template #default="{ row }">
                  {{ formatNumber(row.total_tokens) }}
                </template>
              </el-table-column>
              <el-table-column prop="total_cost" label="费用" width="120">
                <template #default="{ row }">
                  ${{ row.total_cost.toFixed(4) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="viewUserStatus(row.user_id)">
                    查看详情
                  </el-button>
                  <el-button size="small" type="primary" @click="editUserQuota(row.user_id, row.username)">
                    设置配额
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 配额配置 -->
        <el-tab-pane label="配额配置" name="quotas">
          <div class="tab-content">
            <div class="toolbar">
              <el-button type="primary" @click="showAddQuotaDialog">
                <el-icon><Plus /></el-icon>
                新增配额
              </el-button>
            </div>
            
            <el-table :data="quotaList" v-loading="loadingQuotas" stripe>
              <el-table-column prop="target_name" label="目标" width="150" />
              <el-table-column prop="quota_type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.quota_type === 'user' ? 'primary' : 'success'">
                    {{ row.quota_type === 'user' ? '用户' : '团队' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="请求限制" width="200">
                <template #default="{ row }">
                  <div class="limit-info">
                    <span>{{ row.requests_per_day.toLocaleString() }}/天</span>
                    <span>{{ row.requests_per_month.toLocaleString() }}/月</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Token 限制" width="200">
                <template #default="{ row }">
                  <div class="limit-info">
                    <span>{{ formatNumber(row.tokens_per_day) }}/天</span>
                    <span>{{ formatNumber(row.tokens_per_month) }}/月</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="费用限制" width="150">
                <template #default="{ row }">
                  <div class="limit-info">
                    <span>${{ row.cost_per_day }}/天</span>
                    <span>${{ row.cost_per_month }}/月</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'">
                    {{ row.is_active ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button size="small" @click="editQuota(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteQuota(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 配额编辑对话框 -->
    <el-dialog 
      v-model="quotaDialogVisible" 
      :title="editingQuotaId ? '编辑配额' : '新增配额'"
      width="600px"
    >
      <el-form :model="quotaForm" label-width="120px">
        <el-form-item label="目标类型" v-if="!editingQuotaId">
          <el-radio-group v-model="quotaForm.quota_type">
            <el-radio value="user">用户</el-radio>
            <el-radio value="team">团队</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="目标用户" v-if="quotaForm.quota_type === 'user' && !editingQuotaId">
          <el-select v-model="quotaForm.target_id" filterable placeholder="选择用户">
            <el-option 
              v-for="user in userList" 
              :key="user.id" 
              :label="user.username" 
              :value="user.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="目标团队" v-if="quotaForm.quota_type === 'team' && !editingQuotaId">
          <el-input v-model.number="quotaForm.target_id" placeholder="输入团队ID" />
        </el-form-item>

        <el-divider>请求限制</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="每分钟">
              <el-input-number v-model="quotaForm.requests_per_minute" :min="1" :max="10000" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每小时">
              <el-input-number v-model="quotaForm.requests_per_hour" :min="1" :max="100000" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="每天">
              <el-input-number v-model="quotaForm.requests_per_day" :min="1" :max="1000000" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每月">
              <el-input-number v-model="quotaForm.requests_per_month" :min="1" :max="10000000" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>Token 限制</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="每天 Token">
              <el-input-number v-model="quotaForm.tokens_per_day" :min="1000" :step="100000" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每月 Token">
              <el-input-number v-model="quotaForm.tokens_per_month" :min="10000" :step="1000000" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>费用限制 (USD)</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="每天费用">
              <el-input-number v-model="quotaForm.cost_per_day" :min="0.1" :step="1" :precision="2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每月费用">
              <el-input-number v-model="quotaForm.cost_per_month" :min="1" :step="10" :precision="2" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="状态">
          <el-switch v-model="quotaForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="quotaForm.description" type="textarea" placeholder="可选备注" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="quotaDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveQuota" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 用户详情对话框 -->
    <el-dialog v-model="userStatusDialogVisible" title="用户配额详情" width="500px">
      <div v-if="userStatus" class="user-status-detail">
        <div class="status-section">
          <h4>今日使用</h4>
          <div class="status-row">
            <span>请求数</span>
            <span>{{ userStatus.today_requests }} / {{ userStatus.quota?.requests_per_day || '无限制' }}</span>
          </div>
          <div class="status-row">
            <span>Token</span>
            <span>{{ formatNumber(userStatus.today_tokens) }} / {{ formatNumber(userStatus.quota?.tokens_per_day) || '无限制' }}</span>
          </div>
          <div class="status-row">
            <span>费用</span>
            <span>${{ userStatus.today_cost.toFixed(4) }} / ${{ userStatus.quota?.cost_per_day || '无限制' }}</span>
          </div>
        </div>
        
        <div class="status-section">
          <h4>本月使用</h4>
          <div class="status-row">
            <span>请求数</span>
            <el-progress 
              :percentage="userStatus.usage_percent_requests" 
              :color="getProgressColor(userStatus.usage_percent_requests)"
            />
          </div>
          <div class="status-row">
            <span>Token</span>
            <el-progress 
              :percentage="userStatus.usage_percent_tokens" 
              :color="getProgressColor(userStatus.usage_percent_tokens)"
            />
          </div>
          <div class="status-row">
            <span>费用</span>
            <el-progress 
              :percentage="userStatus.usage_percent_cost" 
              :color="getProgressColor(userStatus.usage_percent_cost)"
            />
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Odometer, Connection, Coin, Money, User, Plus } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import request from '@/api/request'

const activeTab = ref('usage')
const loadingUsage = ref(false)
const loadingQuotas = ref(false)
const saving = ref(false)

const usageList = ref<any[]>([])
const quotaList = ref<any[]>([])
const userList = ref<any[]>([])

const quotaDialogVisible = ref(false)
const userStatusDialogVisible = ref(false)
const editingQuotaId = ref<number | null>(null)
const userStatus = ref<any>(null)

const quotaForm = ref({
  quota_type: 'user',
  target_id: null as number | null,
  requests_per_minute: 60,
  requests_per_hour: 1000,
  requests_per_day: 10000,
  requests_per_month: 100000,
  tokens_per_day: 1000000,
  tokens_per_month: 10000000,
  cost_per_day: 10,
  cost_per_month: 100,
  is_active: true,
  description: ''
})

const totalStats = computed(() => {
  const stats = {
    totalRequests: 0,
    totalTokens: 0,
    totalCost: 0,
    activeUsers: usageList.value.length
  }
  
  usageList.value.forEach(u => {
    stats.totalRequests += u.total_requests || 0
    stats.totalTokens += u.total_tokens || 0
    stats.totalCost += u.total_cost || 0
  })
  
  return stats
})

function formatNumber(num: number): string {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function getProgressColor(percent: number): string {
  if (percent >= 90) return '#f56c6c'
  if (percent >= 70) return '#e6a23c'
  return '#67c23a'
}

async function loadUsageData() {
  loadingUsage.value = true
  try {
    const res = await request.get('/api/quota/admin/usage/all', { params: { days: 7 } }) as any
    // 响应拦截器返回 {data, message}
    usageList.value = res.data?.users || []
  } catch (e) {
    console.error('加载使用数据失败:', e)
  } finally {
    loadingUsage.value = false
  }
}

async function loadQuotaList() {
  loadingQuotas.value = true
  try {
    const res = await request.get('/api/quota/admin/list') as any
    // 响应拦截器返回 {data, message}，data 就是数组
    quotaList.value = res.data || []
  } catch (e) {
    console.error('加载配额列表失败:', e)
  } finally {
    loadingQuotas.value = false
  }
}

async function loadUserList() {
  try {
    const res = await request.get('/api/admin/users')
    // 兼容两种返回格式
    if (res.data.code === 0) {
      userList.value = res.data.data?.items || []
    } else if (res.data.items) {
      userList.value = res.data.items
    }
  } catch (e) {
    console.error('加载用户列表失败:', e)
  }
}

async function viewUserStatus(userId: number) {
  try {
    const res = await request.get(`/api/quota/admin/user/${userId}/status`) as any
    // 响应拦截器返回 {data, message}
    userStatus.value = res.data
    userStatusDialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取用户状态失败')
  }
}

function editUserQuota(userId: number, username: string) {
  editingQuotaId.value = null
  quotaForm.value = {
    quota_type: 'user',
    target_id: userId,
    requests_per_minute: 60,
    requests_per_hour: 1000,
    requests_per_day: 10000,
    requests_per_month: 100000,
    tokens_per_day: 1000000,
    tokens_per_month: 10000000,
    cost_per_day: 10,
    cost_per_month: 100,
    is_active: true,
    description: `${username} 的配额`
  }
  quotaDialogVisible.value = true
}

function showAddQuotaDialog() {
  editingQuotaId.value = null
  quotaForm.value = {
    quota_type: 'user',
    target_id: null,
    requests_per_minute: 60,
    requests_per_hour: 1000,
    requests_per_day: 10000,
    requests_per_month: 100000,
    tokens_per_day: 1000000,
    tokens_per_month: 10000000,
    cost_per_day: 10,
    cost_per_month: 100,
    is_active: true,
    description: ''
  }
  quotaDialogVisible.value = true
}

function editQuota(quota: any) {
  editingQuotaId.value = quota.id
  quotaForm.value = {
    quota_type: quota.quota_type,
    target_id: quota.target_id,
    requests_per_minute: quota.requests_per_minute,
    requests_per_hour: quota.requests_per_hour,
    requests_per_day: quota.requests_per_day,
    requests_per_month: quota.requests_per_month,
    tokens_per_day: quota.tokens_per_day,
    tokens_per_month: quota.tokens_per_month,
    cost_per_day: quota.cost_per_day,
    cost_per_month: quota.cost_per_month,
    is_active: quota.is_active,
    description: quota.description || ''
  }
  quotaDialogVisible.value = true
}

async function saveQuota() {
  if (!quotaForm.value.target_id) {
    ElMessage.warning('请选择目标')
    return
  }
  
  saving.value = true
  try {
    const url = quotaForm.value.quota_type === 'user' 
      ? `/api/quota/admin/user/${quotaForm.value.target_id}`
      : `/api/quota/admin/team/${quotaForm.value.target_id}`
    
    const res = await request.post(url, quotaForm.value) as any
    // 响应拦截器已处理，成功时直接返回 {data, message}
    ElMessage.success(res.message || '配额保存成功')
    quotaDialogVisible.value = false
    loadQuotaList()
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    saving.value = false
  }
}

async function deleteQuota(quotaId: number) {
  try {
    await ElMessageBox.confirm('确定删除该配额配置？', '确认删除')
    const res = await request.delete(`/api/quota/admin/${quotaId}`)
    if (res.data.code === 0) {
      ElMessage.success('删除成功')
      loadQuotaList()
    }
  } catch (e) {
    // 取消删除
  }
}

onMounted(() => {
  loadUsageData()
  loadQuotaList()
  loadUserList()
})
</script>

<style scoped>
.quota-manage-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  color: #303133;
  margin: 0 0 8px;
}

.page-header p {
  color: #909399;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.requests {
  background: #e8f4ff;
  color: #409eff;
}

.stat-icon.tokens {
  background: #fdf6ec;
  color: #e6a23c;
}

.stat-icon.cost {
  background: #f0f9eb;
  color: #67c23a;
}

.stat-icon.users {
  background: #fef0f0;
  color: #f56c6c;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.quota-tabs {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.tab-content {
  padding-top: 16px;
}

.toolbar {
  margin-bottom: 16px;
}

.limit-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.limit-info span:first-child {
  color: #303133;
}

.limit-info span:last-child {
  color: #909399;
}

.user-status-detail {
  padding: 0 16px;
}

.status-section {
  margin-bottom: 24px;
}

.status-section h4 {
  font-size: 14px;
  color: #606266;
  margin: 0 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-row span:first-child {
  color: #909399;
  font-size: 13px;
}

.status-row :deep(.el-progress) {
  width: 200px;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
