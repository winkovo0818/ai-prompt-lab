<template>
  <div class="admin-teams-page">
    <Header />
    
    <div class="content">
      <el-card>
        <template #header>
          <div class="card-header">
            <h2>团队管理</h2>
          </div>
        </template>

        <div class="search-bar">
          <el-input v-model="searchText" placeholder="搜索团队名称" clearable @clear="loadTeams" style="width: 300px">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="loadTeams">搜索</el-button>
        </div>

        <el-table :data="teams" style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="团队名称" min-width="150" />
          <el-table-column prop="owner_username" label="所有者" width="120" />
          <el-table-column prop="member_count" label="成员数" width="100" />
          <el-table-column prop="prompt_count" label="Prompt数" width="100" />
          <el-table-column prop="is_public" label="公开" width="80">
            <template #default="scope">
              <el-tag v-if="scope.row.is_public" type="success" size="small">是</el-tag>
              <el-tag v-else type="info" size="small">否</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="viewTeam(scope.row)">查看</el-button>
              <el-button size="small" type="primary" @click="editTeam(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteTeam(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadTeams"
          @size-change="loadTeams"
          style="margin-top: 20px; justify-content: flex-end"
        />
      </el-card>
    </div>

    <!-- 查看团队详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="团队详情" width="700px">
      <div v-if="teamDetail" class="team-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="团队ID">{{ teamDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="团队名称">{{ teamDetail.name }}</el-descriptions-item>
          <el-descriptions-item label="所有者">{{ teamDetail.owner_username }}</el-descriptions-item>
          <el-descriptions-item label="公开">{{ teamDetail.is_public ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ teamDetail.description || '暂无' }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin: 20px 0 10px">成员列表 ({{ teamDetail.members?.length || 0 }})</h4>
        <el-table :data="teamDetail.members" size="small" max-height="200">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="scope">
              <el-tag size="small" :type="getRoleTagType(scope.row.role)">
                {{ getRoleName(scope.row.role) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="scope">
              <el-button 
                v-if="scope.row.role !== 'owner'" 
                size="small" 
                type="danger" 
                text
                @click="removeMember(scope.row)"
              >
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <h4 style="margin: 20px 0 10px">共享 Prompt ({{ teamDetail.prompts?.length || 0 }})</h4>
        <el-table :data="teamDetail.prompts" size="small" max-height="200">
          <el-table-column prop="prompt_id" label="ID" width="80" />
          <el-table-column prop="prompt_title" label="标题" />
          <el-table-column prop="permission" label="权限" width="100">
            <template #default="scope">
              <el-tag size="small" :type="scope.row.permission === 'edit' ? 'success' : 'info'">
                {{ scope.row.permission === 'edit' ? '可编辑' : '只读' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 编辑团队对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑团队" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="团队名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="公开团队">
          <el-switch v-model="editForm.is_public" />
        </el-form-item>
        <el-form-item label="成员可邀请">
          <el-switch v-model="editForm.allow_member_invite" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { adminAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'

const loading = ref(false)
const submitting = ref(false)
const teams = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchText = ref('')

const detailDialogVisible = ref(false)
const editDialogVisible = ref(false)
const teamDetail = ref<any>(null)
const currentTeamId = ref<number | null>(null)

const editForm = reactive({
  name: '',
  description: '',
  is_public: false,
  allow_member_invite: false
})

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getRoleName(role: string) {
  const names: Record<string, string> = {
    owner: '所有者',
    editor: '编辑者',
    viewer: '查看者'
  }
  return names[role] || role
}

function getRoleTagType(role: string) {
  const types: Record<string, string> = {
    owner: 'danger',
    editor: 'warning',
    viewer: 'info'
  }
  return types[role] || 'info'
}

async function loadTeams() {
  loading.value = true
  try {
    const res = await adminAPI.getTeams({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchText.value || undefined
    }) as any
    teams.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    console.error('加载团队失败:', error)
  } finally {
    loading.value = false
  }
}

async function viewTeam(team: any) {
  try {
    const res = await adminAPI.getTeamDetail(team.id) as any
    teamDetail.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    console.error('加载团队详情失败:', error)
  }
}

function editTeam(team: any) {
  currentTeamId.value = team.id
  editForm.name = team.name
  editForm.description = team.description || ''
  editForm.is_public = team.is_public
  editForm.allow_member_invite = team.allow_member_invite || false
  editDialogVisible.value = true
}

async function submitEdit() {
  if (!currentTeamId.value) return
  
  submitting.value = true
  try {
    await adminAPI.updateTeam(currentTeamId.value, editForm)
    ElMessage.success('团队更新成功')
    editDialogVisible.value = false
    await loadTeams()
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    submitting.value = false
  }
}

async function deleteTeam(team: any) {
  try {
    await ElMessageBox.confirm(
      `确定要删除团队 "${team.name}" 吗？此操作将删除所有成员和共享的 Prompt 关联，不可恢复！`,
      '删除确认',
      { type: 'warning' }
    )
    
    await adminAPI.deleteTeam(team.id)
    ElMessage.success('团队已删除')
    await loadTeams()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

async function removeMember(member: any) {
  if (!teamDetail.value) return
  
  try {
    await ElMessageBox.confirm(`确定要移除成员 "${member.username}" 吗？`, '移除确认', {
      type: 'warning'
    })
    
    await adminAPI.removeTeamMember(teamDetail.value.id, member.id)
    ElMessage.success('成员已移除')
    // 刷新详情
    await viewTeam({ id: teamDetail.value.id })
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '移除失败')
    }
  }
}

onMounted(() => {
  loadTeams()
})
</script>

<style scoped>
.admin-teams-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.content {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.team-detail h4 {
  color: #303133;
  font-size: 14px;
}
</style>
