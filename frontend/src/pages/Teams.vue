<template>
  <div class="teams-page">
    <Header />
    
    <div class="page-content">
      <div class="page-header">
        <h1>团队工作区</h1>
        <div class="header-actions">
          <div class="join-input-wrapper">
            <el-input
              v-model="joinCode"
              placeholder="粘贴邀请码"
              class="join-input"
              clearable
            />
            <el-button 
              @click="handleJoinByCode" 
              :loading="joining"
              :disabled="!joinCode.trim()"
              class="join-btn"
            >
              加入团队
            </el-button>
          </div>
          <el-button type="primary" @click="showCreateDialog" class="create-btn">
            <el-icon><Plus /></el-icon>
            创建团队
          </el-button>
        </div>
      </div>

      <!-- 团队列表 -->
      <div v-if="teams.length > 0" class="teams-grid" v-loading="loading">
        <div 
          v-for="team in teams" 
          :key="team.id" 
          class="team-card"
          @click="selectTeam(team)"
        >
          <div class="team-avatar">
            <el-avatar :size="48" :src="team.avatar_url" class="team-avatar-inner">
              {{ team.name.charAt(0).toUpperCase() }}
            </el-avatar>
          </div>
          <div class="team-info">
            <div class="team-name">{{ team.name }}</div>
            <div class="team-desc" :class="{ 'no-desc': !team.description }">
                {{ team.description || '暂无描述' }}
              </div>
            <div class="team-meta">
              <span><el-icon><User /></el-icon> {{ team.member_count }} 成员</span>
              <span><el-icon><Document /></el-icon> {{ team.prompt_count }} Prompt</span>
              <el-tag size="small" :type="getRoleTagType(team.my_role)">
                {{ getRoleName(team.my_role) }}
              </el-tag>
            </div>
          </div>
          <div class="team-actions" @click.stop>
            <el-dropdown v-if="team.my_role === 'owner'" trigger="click">
              <el-button text>
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="editTeam(team)">
                    <el-icon><Edit /></el-icon> 编辑
                  </el-dropdown-item>
                  <el-dropdown-item @click="deleteTeam(team)" divided>
                    <el-icon><Delete /></el-icon> 删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="80" fill="#EBF5FF"/>
            <circle cx="70" cy="85" r="25" fill="#409EFF"/>
            <circle cx="130" cy="85" r="25" fill="#67C23A"/>
            <circle cx="100" cy="130" r="25" fill="#E6A23C"/>
            <circle cx="70" cy="85" r="12" fill="white"/>
            <circle cx="130" cy="85" r="12" fill="white"/>
            <circle cx="100" cy="130" r="12" fill="white"/>
            <path d="M70 85 L100 110 L130 85" stroke="#409EFF" stroke-width="3" stroke-linecap="round"/>
            <path d="M100 110 L100 130" stroke="#409EFF" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>
        <h2 class="empty-title">开始团队协作</h2>
        <p class="empty-desc">创建团队来与同事共享 Prompt，实现高效协作</p>
        <div class="empty-features">
          <div class="feature-item">
            <el-icon class="feature-icon"><User /></el-icon>
            <span>邀请成员加入</span>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Document /></el-icon>
            <span>共享 Prompt 库</span>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Edit /></el-icon>
            <span>灵活的权限控制</span>
          </div>
        </div>
        <div class="empty-actions">
          <el-button type="primary" size="large" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            创建我的第一个团队
          </el-button>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-else class="loading-state">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <p>加载中...</p>
      </div>

      <!-- 团队详情抽屉 -->
      <el-drawer
        v-model="drawerVisible"
        :title="selectedTeam?.name"
        size="600px"
        direction="rtl"
      >
        <div v-if="selectedTeam" class="team-detail">
          <el-tabs v-model="activeTab">
            <!-- 成员管理 -->
            <el-tab-pane label="成员" name="members">
              <div class="tab-header">
                <span>{{ members.length }} 位成员</span>
                <el-button 
                  v-if="canManageMembers" 
                  size="small" 
                  type="primary"
                  @click="showAddMemberDialog"
                >
                  <el-icon><Plus /></el-icon> 添加成员
                </el-button>
              </div>
              
              <div class="members-list">
                <div v-for="member in members" :key="member.id" class="member-item">
                  <el-avatar :size="36" :src="member.avatar_url">
                    {{ member.username.charAt(0).toUpperCase() }}
                  </el-avatar>
                  <div class="member-info">
                    <div class="member-name">{{ member.username }}</div>
                    <div class="member-email">{{ member.email }}</div>
                  </div>
                  <el-tag :type="getRoleTagType(member.role)" size="small">
                    {{ getRoleName(member.role) }}
                  </el-tag>
                  <div class="member-actions" v-if="canManageMembers && member.role !== 'owner'">
                    <el-dropdown trigger="click">
                      <el-button text size="small">
                        <el-icon><MoreFilled /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click="changeMemberRole(member, 'editor')">
                            设为编辑者
                          </el-dropdown-item>
                          <el-dropdown-item @click="changeMemberRole(member, 'viewer')">
                            设为查看者
                          </el-dropdown-item>
                          <el-dropdown-item @click="removeMember(member)" divided>
                            <span class="text-red-500">移除成员</span>
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- Prompt 库 -->
            <el-tab-pane label="Prompt 库" name="prompts">
              <div class="tab-header">
                <span>{{ teamPrompts.length }} 个 Prompt</span>
                <el-button 
                  v-if="canEditPrompts" 
                  size="small" 
                  type="primary"
                  @click="showSharePromptDialog"
                >
                  <el-icon><Share /></el-icon> 共享 Prompt
                </el-button>
              </div>
              
              <div class="prompts-list">
                <div v-for="tp in teamPrompts" :key="tp.id" class="prompt-card" @click="openPrompt(tp)">
                  <div class="prompt-card-header">
                    <div class="prompt-icon">
                      <el-icon><Document /></el-icon>
                    </div>
                    <div class="prompt-title-wrapper">
                      <div class="prompt-title">{{ tp.prompt_title }}</div>
                      <el-tag size="small" :type="tp.permission === 'edit' ? 'success' : 'info'">
                        {{ tp.permission === 'edit' ? '可编辑' : '只读' }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="prompt-desc" v-if="tp.prompt_description">
                    {{ tp.prompt_description }}
                  </div>
                  <div class="prompt-card-footer">
                    <div class="prompt-sharer">
                      <el-avatar :size="20">{{ tp.shared_by_username?.charAt(0) }}</el-avatar>
                      <span>{{ tp.shared_by_username }}</span>
                    </div>
                    <div class="prompt-card-actions" @click.stop>
                      <el-button size="small" type="primary" plain @click="openPrompt(tp)">
                        <el-icon><View /></el-icon> 打开
                      </el-button>
                      <el-button 
                        v-if="canEditPrompts" 
                        size="small" 
                        type="danger" 
                        plain
                        @click="removeTeamPrompt(tp)"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
                <el-empty v-if="teamPrompts.length === 0" description="暂无共享的 Prompt">
                  <template #image>
                    <el-icon :size="60" color="#c0c4cc"><Document /></el-icon>
                  </template>
                </el-empty>
              </div>
            </el-tab-pane>

            <!-- 邀请链接 -->
            <el-tab-pane label="邀请" name="invites" v-if="canManageMembers">
              <div class="invite-section">
                <h4>生成邀请链接</h4>
                <el-form :model="inviteForm" label-width="80px">
                  <el-form-item label="角色">
                    <el-select v-model="inviteForm.role" style="width: 150px">
                      <el-option value="viewer" label="查看者" />
                      <el-option value="editor" label="编辑者" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="有效期">
                    <el-select v-model="inviteForm.expires_hours" style="width: 150px">
                      <el-option :value="24" label="24 小时" />
                      <el-option :value="72" label="3 天" />
                      <el-option :value="168" label="7 天" />
                      <el-option :value="720" label="30 天" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="使用次数">
                    <el-input-number v-model="inviteForm.max_uses" :min="1" :max="100" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="generateInvite" :loading="generatingInvite">
                      生成链接
                    </el-button>
                  </el-form-item>
                </el-form>
                
                <div v-if="inviteCode" class="invite-result">
                  <el-input v-model="inviteCode" readonly>
                    <template #append>
                      <el-button @click="copyInviteCode">复制</el-button>
                    </template>
                  </el-input>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-drawer>

      <!-- 创建/编辑团队对话框 -->
      <el-dialog 
        v-model="createDialogVisible" 
        :title="editingTeam ? '编辑团队' : '创建团队'"
        width="500px"
      >
        <el-form :model="teamForm" label-width="100px">
          <el-form-item label="团队名称" required>
            <el-input v-model="teamForm.name" placeholder="输入团队名称" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input 
              v-model="teamForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="团队描述（可选）"
            />
          </el-form-item>
          <el-form-item label="公开团队">
            <el-switch v-model="teamForm.is_public" />
            <span class="form-tip">公开团队对所有人可见</span>
          </el-form-item>
          <el-form-item label="成员可邀请">
            <el-switch v-model="teamForm.allow_member_invite" />
            <span class="form-tip">允许非所有者邀请新成员</span>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTeam" :loading="submitting">
            {{ editingTeam ? '保存' : '创建' }}
          </el-button>
        </template>
      </el-dialog>

      <!-- 添加成员对话框 -->
      <el-dialog v-model="addMemberDialogVisible" title="添加成员" width="400px">
        <el-form :model="memberForm" label-width="80px">
          <el-form-item label="邮箱">
            <el-input v-model="memberForm.email" placeholder="输入用户邮箱" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="memberForm.role" style="width: 100%">
              <el-option value="viewer" label="查看者" />
              <el-option value="editor" label="编辑者" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="addMemberDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAddMember" :loading="submitting">添加</el-button>
        </template>
      </el-dialog>

      <!-- 共享 Prompt 对话框 -->
      <el-dialog v-model="sharePromptDialogVisible" title="共享 Prompt 到团队" width="480px">
        <el-form :model="shareForm" label-position="top">
          <el-form-item label="选择要共享的 Prompt">
            <el-select 
              v-model="shareForm.prompt_id" 
              filterable 
              remote 
              :remote-method="searchPrompts"
              :loading="searchingPrompts"
              placeholder="输入关键词搜索..."
              style="width: 100%"
              size="large"
            >
              <el-option
                v-for="p in myPrompts"
                :key="p.id"
                :value="p.id"
                :label="p.title"
              >
                <div class="prompt-option">
                  <span class="prompt-option-title">{{ p.title }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="共享权限">
            <el-radio-group v-model="shareForm.permission" class="permission-radio-group">
              <el-radio value="view" border>
                <div class="permission-option">
                  <strong>只读</strong>
                  <span>成员可查看但不能编辑</span>
                </div>
              </el-radio>
              <el-radio value="edit" border>
                <div class="permission-option">
                  <strong>可编辑</strong>
                  <span>成员可查看和编辑</span>
                </div>
              </el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="sharePromptDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitSharePrompt" :loading="submitting">
            <el-icon><Share /></el-icon> 共享到团队
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { teamAPI, promptAPI, TeamInfo, TeamMember, TeamPromptItem } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, Document, MoreFilled, Edit, Delete, Share, Loading, View } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const joining = ref(false)
const generatingInvite = ref(false)
const searchingPrompts = ref(false)

const teams = ref<TeamInfo[]>([])
const selectedTeam = ref<TeamInfo | null>(null)
const members = ref<TeamMember[]>([])
const teamPrompts = ref<TeamPromptItem[]>([])
const myPrompts = ref<any[]>([])

const drawerVisible = ref(false)
const activeTab = ref('members')
const createDialogVisible = ref(false)
const addMemberDialogVisible = ref(false)
const sharePromptDialogVisible = ref(false)
const editingTeam = ref<TeamInfo | null>(null)

const joinCode = ref('')
const inviteCode = ref('')

const teamForm = reactive({
  name: '',
  description: '',
  is_public: false,
  allow_member_invite: false
})

const memberForm = reactive({
  email: '',
  role: 'viewer'
})

const shareForm = reactive({
  prompt_id: null as number | null,
  permission: 'view'
})

const inviteForm = reactive({
  role: 'viewer',
  expires_hours: 72,
  max_uses: 10
})

const canManageMembers = computed(() => 
  selectedTeam.value?.my_role === 'owner'
)

const canEditPrompts = computed(() => 
  selectedTeam.value?.my_role === 'owner' || selectedTeam.value?.my_role === 'editor'
)

function getRoleName(role?: string) {
  const names: Record<string, string> = {
    owner: '所有者',
    editor: '编辑者',
    viewer: '查看者'
  }
  return names[role || ''] || role
}

function getRoleTagType(role?: string) {
  const types: Record<string, string> = {
    owner: 'danger',
    editor: 'warning',
    viewer: 'info'
  }
  return types[role || ''] || 'info'
}

async function loadTeams() {
  loading.value = true
  try {
    const res = await teamAPI.getMyTeams() as any
    teams.value = res.data || []
  } catch (error) {
    console.error('加载团队失败:', error)
  } finally {
    loading.value = false
  }
}

async function selectTeam(team: TeamInfo) {
  selectedTeam.value = team
  drawerVisible.value = true
  activeTab.value = 'members'
  await Promise.all([loadMembers(team.id), loadTeamPrompts(team.id)])
}

async function loadMembers(teamId: number) {
  try {
    const res = await teamAPI.getMembers(teamId) as any
    members.value = res.data || []
  } catch (error) {
    console.error('加载成员失败:', error)
  }
}

async function loadTeamPrompts(teamId: number) {
  try {
    const res = await teamAPI.getTeamPrompts(teamId) as any
    teamPrompts.value = res.data?.items || []
  } catch (error) {
    console.error('加载 Prompt 失败:', error)
  }
}

function showCreateDialog() {
  editingTeam.value = null
  teamForm.name = ''
  teamForm.description = ''
  teamForm.is_public = false
  teamForm.allow_member_invite = false
  createDialogVisible.value = true
}

function editTeam(team: TeamInfo) {
  editingTeam.value = team
  teamForm.name = team.name
  teamForm.description = team.description || ''
  teamForm.is_public = team.is_public
  teamForm.allow_member_invite = team.allow_member_invite
  createDialogVisible.value = true
}

async function submitTeam() {
  if (!teamForm.name.trim()) {
    ElMessage.warning('请输入团队名称')
    return
  }
  
  submitting.value = true
  try {
    if (editingTeam.value) {
      await teamAPI.updateTeam(editingTeam.value.id, teamForm)
      ElMessage.success('团队更新成功')
    } else {
      await teamAPI.createTeam(teamForm)
      ElMessage.success('团队创建成功')
    }
    createDialogVisible.value = false
    await loadTeams()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function deleteTeam(team: TeamInfo) {
  try {
    await ElMessageBox.confirm(`确定要删除团队 "${team.name}" 吗？此操作不可恢复。`, '删除确认', {
      type: 'warning'
    })
    
    await teamAPI.deleteTeam(team.id)
    ElMessage.success('团队已删除')
    await loadTeams()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

function showAddMemberDialog() {
  memberForm.email = ''
  memberForm.role = 'viewer'
  addMemberDialogVisible.value = true
}

async function submitAddMember() {
  if (!memberForm.email.trim()) {
    ElMessage.warning('请输入邮箱')
    return
  }
  
  submitting.value = true
  try {
    await teamAPI.addMember(selectedTeam.value!.id, {
      email: memberForm.email,
      role: memberForm.role
    })
    ElMessage.success('成员添加成功')
    addMemberDialogVisible.value = false
    await loadMembers(selectedTeam.value!.id)
  } catch (error: any) {
    ElMessage.error(error.message || '添加失败')
  } finally {
    submitting.value = false
  }
}

async function changeMemberRole(member: TeamMember, newRole: string) {
  try {
    await teamAPI.updateMember(selectedTeam.value!.id, member.id, { role: newRole })
    ElMessage.success('角色更新成功')
    await loadMembers(selectedTeam.value!.id)
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  }
}

async function removeMember(member: TeamMember) {
  try {
    await ElMessageBox.confirm(`确定要移除成员 "${member.username}" 吗？`, '移除确认', {
      type: 'warning'
    })
    
    await teamAPI.removeMember(selectedTeam.value!.id, member.id)
    ElMessage.success('成员已移除')
    await loadMembers(selectedTeam.value!.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '移除失败')
    }
  }
}

async function searchPrompts(query: string) {
  if (!query) return
  
  searchingPrompts.value = true
  try {
    const res = await promptAPI.getList({ search: query, limit: 20 }) as any
    myPrompts.value = res.data?.items || []
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    searchingPrompts.value = false
  }
}

function showSharePromptDialog() {
  shareForm.prompt_id = null
  shareForm.permission = 'view'
  myPrompts.value = []
  sharePromptDialogVisible.value = true
}

async function submitSharePrompt() {
  if (!shareForm.prompt_id) {
    ElMessage.warning('请选择 Prompt')
    return
  }
  
  submitting.value = true
  try {
    await teamAPI.sharePrompt(selectedTeam.value!.id, {
      prompt_id: shareForm.prompt_id,
      permission: shareForm.permission
    })
    ElMessage.success('Prompt 已共享到团队')
    sharePromptDialogVisible.value = false
    await loadTeamPrompts(selectedTeam.value!.id)
  } catch (error: any) {
    ElMessage.error(error.message || '共享失败')
  } finally {
    submitting.value = false
  }
}

async function removeTeamPrompt(tp: TeamPromptItem) {
  try {
    await ElMessageBox.confirm('确定要从团队移除此 Prompt 吗？', '移除确认', {
      type: 'warning'
    })
    
    await teamAPI.removePrompt(selectedTeam.value!.id, tp.id)
    ElMessage.success('已移除')
    await loadTeamPrompts(selectedTeam.value!.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '移除失败')
    }
  }
}

function openPrompt(tp: TeamPromptItem) {
  router.push(`/editor/${tp.prompt_id}`)
}

async function generateInvite() {
  generatingInvite.value = true
  try {
    const res = await teamAPI.createInvite(selectedTeam.value!.id, inviteForm) as any
    const code = res.data?.invite_code || ''
    // 生成完整的邀请链接
    inviteCode.value = `${window.location.origin}/teams?join=${code}`
    ElMessage.success('邀请链接已生成')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败')
  } finally {
    generatingInvite.value = false
  }
}

function copyInviteCode() {
  navigator.clipboard.writeText(inviteCode.value)
  ElMessage.success('已复制到剪贴板')
}

async function handleJoinByCode() {
  if (!joinCode.value.trim()) {
    ElMessage.warning('请输入邀请码')
    return
  }
  
  joining.value = true
  try {
    const res = await teamAPI.joinByInvite(joinCode.value) as any
    ElMessage.success(`已成功加入团队: ${res.data?.team_name}`)
    joinCode.value = ''
    await loadTeams()
  } catch (error: any) {
    // 错误已在 axios 拦截器中处理，这里不再重复显示
    console.log('加入团队失败:', error)
  } finally {
    joining.value = false
  }
}

onMounted(async () => {
  await loadTeams()
  
  // 检查 URL 是否有邀请码参数
  const urlParams = new URLSearchParams(window.location.search)
  const joinParam = urlParams.get('join')
  if (joinParam) {
    joinCode.value = joinParam
    // 清除 URL 参数
    window.history.replaceState({}, '', '/teams')
    // 自动尝试加入
    await handleJoinByCode()
  }
})
</script>

<style scoped>
.teams-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 3rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e8ecf0;
}

.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-header h1::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #409eff 0%, #36b3ff 100%);
  border-radius: 2px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.join-input-wrapper {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  padding: 2px;
  transition: all 0.2s;
}

.join-input-wrapper:focus-within {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.join-input :deep(.el-input__wrapper) {
  box-shadow: none !important;
  background: transparent;
}

.join-input {
  width: 180px;
}

.join-btn {
  border-radius: 6px;
  margin-right: 2px;
}

.create-btn {
  border-radius: 8px;
  padding: 10px 20px;
}

/* 团队网格 */
.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
}

.team-card {
  display: flex;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: white;
  border-radius: 12px;
  border: 1px solid #e4e8ee;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.team-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
  transform: translateY(-1px);
}

.team-avatar {
  flex-shrink: 0;
}

.team-avatar-inner {
  background: linear-gradient(135deg, #409eff 0%, #36b3ff 100%);
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.team-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.team-name {
  font-size: 1.15rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.35rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.team-desc {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.75rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.5;
}

.team-desc.no-desc {
  color: #b0bac5;
  font-style: italic;
}

.team-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  font-size: 0.75rem;
  color: #64748b;
}

.team-meta span {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: #f1f5f9;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.team-meta span .el-icon {
  color: #94a3b8;
  font-size: 0.8rem;
}

.team-meta .el-tag {
  margin-left: auto;
}

.team-actions {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.team-card:hover .team-actions {
  opacity: 1;
}

/* 抽屉内容 */
.team-detail {
  height: 100%;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e4e7ed;
}

/* 成员列表 */
.members-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.member-info {
  flex: 1;
}

.member-name {
  font-weight: 600;
  color: #1e293b;
}

.member-email {
  font-size: 0.8rem;
  color: #64748b;
}

/* Prompt 列表 */
.prompts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.prompt-card {
  background: #f8fafc;
  border: 1px solid transparent;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.prompt-card:hover {
  background: white;
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.08);
}

.prompt-card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.prompt-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #409eff 0%, #36b3ff 100%);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.prompt-title-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.prompt-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prompt-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin-left: 2.5rem;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.prompt-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-left: 2.5rem;
  padding-top: 0.5rem;
}

.prompt-sharer {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.prompt-sharer .el-avatar {
  background: #e2e8f0;
  color: #64748b;
  font-size: 0.65rem;
}

.prompt-card-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.prompt-card:hover .prompt-card-actions {
  opacity: 1;
}

/* 邀请区域 */
.invite-section h4 {
  margin: 0 0 1rem 0;
  color: #1e293b;
}

.invite-result {
  margin-top: 1rem;
  padding: 1rem;
  background: #f0fdf4;
  border-radius: 8px;
}

.form-tip {
  margin-left: 0.5rem;
  font-size: 0.8rem;
  color: #94a3b8;
}

/* 共享对话框样式 */
.permission-radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
}

.permission-radio-group .el-radio {
  margin-right: 0;
  width: 100%;
  height: auto;
  padding: 0.75rem 1rem;
}

.permission-option {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.permission-option strong {
  font-size: 0.9rem;
  color: #1e293b;
}

.permission-option span {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: normal;
}

.prompt-option {
  padding: 0.25rem 0;
}

.prompt-option-title {
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  padding: 3rem;
  background: white;
  border-radius: 16px;
  text-align: center;
}

.empty-icon {
  width: 180px;
  height: 180px;
  margin-bottom: 1.5rem;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.75rem 0;
}

.empty-desc {
  font-size: 1rem;
  color: #64748b;
  margin: 0 0 2rem 0;
  max-width: 400px;
}

.empty-features {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-radius: 12px;
  color: #475569;
  font-size: 0.9rem;
}

.feature-icon {
  font-size: 1.5rem;
  color: #409eff;
}

.empty-actions {
  display: flex;
  gap: 1rem;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #64748b;
}

.loading-state p {
  margin-top: 1rem;
}

/* 团队头像 */
.team-avatar-inner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 1.25rem;
}
</style>
