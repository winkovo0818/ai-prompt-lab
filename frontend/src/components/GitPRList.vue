<template>
  <div class="pr-list">
    <div class="pr-header">
      <h4>Pull Requests</h4>
      <el-button size="small" type="primary" @click="showCreateDialog = true">
        <el-icon><plus /></el-icon> 创建 PR
      </el-button>
    </div>

    <el-tabs v-model="activeStatus" @tab-change="handleStatusChange">
      <el-tab-pane label="Open" name="open" />
      <el-tab-pane label="Merged" name="merged" />
      <el-tab-pane label="Closed" name="closed" />
    </el-tabs>

    <div class="pr-list-content" v-loading="loading">
      <div v-if="prs.length === 0" class="empty-state">
        暂无 PR
      </div>

      <div
        v-for="pr in prs"
        :key="pr.id"
        class="pr-item"
        @click="handleSelectPR(pr)"
      >
        <div class="pr-info">
          <el-tag :type="getStatusType(pr.status)" size="small">{{ pr.status }}</el-tag>
          <span class="pr-title">{{ pr.title }}</span>
        </div>
        <div class="pr-meta">
          <span>{{ pr.source_branch?.name }} → {{ pr.target_branch?.name }}</span>
          <span class="pr-time">{{ formatTime(pr.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- 创建 PR 对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建 Pull Request" width="500px">
      <el-form :model="prForm" label-width="100px">
        <el-form-item label="源分支">
          <el-select v-model="prForm.source_branch_id" placeholder="选择源分支">
            <el-option v-for="b in branches" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标分支">
          <el-select v-model="prForm.target_branch_id" placeholder="选择目标分支">
            <el-option v-for="b in branches" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="prForm.title" placeholder="PR 标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="prForm.description" type="textarea" placeholder="PR 描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreatePR">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getPullRequests, createPullRequest, getBranches } from '@/api/git'

const props = defineProps<{
  promptId: number
}>()

const emit = defineEmits<{
  (e: 'select', pr: any): void
}>()

const activeStatus = ref('open')
const prs = ref<any[]>([])
const branches = ref<any[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const prForm = ref({
  source_branch_id: null as number | null,
  target_branch_id: null as number | null,
  title: '',
  description: ''
})

const loadPRs = async () => {
  loading.value = true
  try {
    const res = await getPullRequests(props.promptId, activeStatus.value)
    prs.value = res.data?.items || []
  } catch (err) {
    console.error('加载 PR 失败', err)
  } finally {
    loading.value = false
  }
}

const loadBranches = async () => {
  try {
    const res = await getBranches(props.promptId)
    branches.value = res.data || []
  } catch (err) {
    console.error('加载分支失败', err)
  }
}

const handleStatusChange = () => {
  loadPRs()
}

const handleSelectPR = (pr: any) => {
  emit('select', pr)
}

const handleCreatePR = async () => {
  if (!prForm.value.source_branch_id || !prForm.value.target_branch_id) {
    ElMessage.warning('请选择源分支和目标分支')
    return
  }
  if (!prForm.value.title) {
    ElMessage.warning('请输入 PR 标题')
    return
  }
  try {
    await createPullRequest(props.promptId, prForm.value)
    ElMessage.success('PR 创建成功')
    showCreateDialog.value = false
    loadPRs()
  } catch (err) {
    console.error('创建 PR 失败', err)
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'open': return 'success'
    case 'merged': return 'info'
    case 'closed': return 'danger'
    default: return 'info'
  }
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN', { month: 'short', day: 'numeric' })
}

onMounted(() => {
  loadPRs()
  loadBranches()
})
</script>

<style scoped>
.pr-list {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}
.pr-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.pr-header h4 {
  margin: 0;
}
.pr-list-content {
  margin-top: 12px;
}
.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 0;
}
.pr-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.pr-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
}
.pr-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.pr-title {
  font-weight: 500;
  color: #333;
}
.pr-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}
</style>