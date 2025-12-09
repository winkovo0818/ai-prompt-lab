<template>
  <div class="profile-page">
    <Header />
    
    <div class="content-container">
      <!-- 用户头像和基本信息 -->
      <div class="profile-header">
        <div class="avatar-section">
          <div class="avatar-upload">
            <el-avatar 
              :size="100" 
              class="user-avatar"
              :src="avatarUrl"
            >
              {{ userStore.userInfo?.username?.[0]?.toUpperCase() || 'U' }}
            </el-avatar>
            <div class="avatar-overlay" @click="triggerUpload">
              <el-icon><Camera /></el-icon>
              <span>更换头像</span>
            </div>
            <input 
              ref="avatarInput"
              type="file" 
              accept="image/jpeg,image/png,image/gif,image/webp"
              style="display: none"
              @change="handleAvatarChange"
            />
          </div>
          <div class="user-info">
            <h2 class="username">{{ userStore.userInfo?.username }}</h2>
            <div class="user-meta">
              <el-tag v-if="userStore.userInfo?.role === 'admin'" type="success" effect="dark">
                <el-icon><Star /></el-icon>
                <span>管理员</span>
              </el-tag>
              <el-tag v-else type="info" effect="plain">普通用户</el-tag>
              <span class="join-date">
                <el-icon><Clock /></el-icon>
                加入时间: {{ formatDate(userStore.userInfo?.created_at) }}
              </span>
            </div>
          </div>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon prompt-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.promptCount }}</div>
              <div class="stat-label">我的 Prompt</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon favorite-icon">
              <el-icon><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.favoriteCount }}</div>
              <div class="stat-label">收藏数量</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon public-icon">
              <el-icon><Share /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.publicCount }}</div>
              <div class="stat-label">公开分享</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 个人资料编辑 -->
      <el-card class="profile-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon class="header-icon"><User /></el-icon>
              <span class="header-title">个人资料</span>
            </div>
            <el-text type="info" size="small">更新您的账户信息</el-text>
          </div>
        </template>

        <el-form 
          ref="formRef"
          :model="profileForm" 
          :rules="formRules"
          label-width="100px" 
          class="profile-form"
        >
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="userStore.userInfo.username" 
              disabled 
              placeholder="用户名不可修改"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="昵称" prop="nickname">
            <el-input 
              v-model="profileForm.nickname" 
              placeholder="请输入昵称"
              clearable
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="profileForm.email" 
              placeholder="请输入邮箱"
              type="email"
            >
              <template #prefix>
                <el-icon><Message /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="手机号" prop="phone">
            <el-input 
              v-model="profileForm.phone" 
              placeholder="请输入手机号"
              clearable
            >
              <template #prefix>
                <el-icon><Phone /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="公司/组织" prop="company">
            <el-input 
              v-model="profileForm.company" 
              placeholder="请输入公司或组织"
              clearable
            >
              <template #prefix>
                <el-icon><OfficeBuilding /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="所在地" prop="location">
            <el-input 
              v-model="profileForm.location" 
              placeholder="请输入所在地"
              clearable
            >
              <template #prefix>
                <el-icon><Location /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="个人网站" prop="website">
            <el-input 
              v-model="profileForm.website" 
              placeholder="请输入个人网站或博客地址"
              clearable
            >
              <template #prefix>
                <el-icon><Link /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="个人简介" prop="bio">
            <el-input 
              v-model="profileForm.bio" 
              type="textarea"
              :rows="4"
              placeholder="介绍一下自己吧..."
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="loading">
              保存修改
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 安全设置 -->
      <el-card class="security-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon class="header-icon"><Lock /></el-icon>
              <span class="header-title">安全设置</span>
            </div>
          </div>
        </template>

        <div class="security-actions">
          <el-button type="primary" @click="goToSecurity">
            <el-icon><Lock /></el-icon>
            修改密码
          </el-button>
        </div>
      </el-card>

      <!-- 账户信息 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon class="header-icon"><InfoFilled /></el-icon>
              <span class="header-title">账户信息</span>
            </div>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID" label-align="right">
            <el-tag>{{ userStore.userInfo?.id }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="账户角色" label-align="right">
            <el-tag v-if="userStore.userInfo?.role === 'admin'" type="success">管理员</el-tag>
            <el-tag v-else type="info">普通用户</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间" label-align="right">
            {{ formatDate(userStore.userInfo?.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后更新" label-align="right">
            {{ formatDate(userStore.userInfo?.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="账户状态" label-align="right">
            <el-tag v-if="userStore.userInfo?.is_active" type="success">正常</el-tag>
            <el-tag v-else type="danger">已禁用</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="登录次数" label-align="right">
            {{ userStore.userInfo?.login_count || 0 }} 次
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { authAPI, promptAPI } from '@/api'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { 
  User, Message, Lock, Star, Clock, Document, Share, InfoFilled, 
  Calendar, Key, Phone, OfficeBuilding, Location, Link, Camera
} from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const avatarInput = ref<HTMLInputElement>()

// 头像相关
const avatarUrl = ref('')
const avatarUploading = ref(false)

const profileForm = ref({
  email: '',
  nickname: '',
  phone: '',
  company: '',
  location: '',
  website: '',
  bio: ''
})

const loading = ref(false)

// 统计数据
const stats = reactive({
  promptCount: 0,
  favoriteCount: 0,
  publicCount: 0
})

// 表单验证规则
const validateEmail = (rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('邮箱不能为空'))
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    callback()
  }
}

const formRules: FormRules = {
  email: [{ validator: validateEmail, trigger: 'blur' }]
}

onMounted(async () => {
  // 先从后端获取最新的用户信息
  await loadUserInfo()
  await loadStats()
})

// 加载用户信息
async function loadUserInfo() {
  try {
    const response = await authAPI.getCurrentUser() as any
    console.log('获取用户信息响应:', response)
    
    // 响应格式是 { data: {...}, message: '...' }，没有 code 字段
    if (response.data) {
      console.log('用户数据:', response.data)
      // 更新 store
      Object.assign(userStore.userInfo || {}, response.data)
      
      // 填充表单
      profileForm.value.email = response.data.email || ''
      profileForm.value.nickname = response.data.nickname || ''
      profileForm.value.phone = response.data.phone || ''
      profileForm.value.company = response.data.company || ''
      profileForm.value.location = response.data.location || ''
      profileForm.value.website = response.data.website || ''
      profileForm.value.bio = response.data.bio || ''
      
      // 初始化头像 URL
      if (response.data.avatar_url) {
        avatarUrl.value = response.data.avatar_url
      }
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    // 降级使用本地数据
    if (userStore.userInfo) {
      profileForm.value.email = userStore.userInfo.email || ''
      profileForm.value.nickname = (userStore.userInfo as any).nickname || ''
      profileForm.value.phone = (userStore.userInfo as any).phone || ''
      profileForm.value.company = (userStore.userInfo as any).company || ''
      profileForm.value.location = (userStore.userInfo as any).location || ''
      profileForm.value.website = (userStore.userInfo as any).website || ''
      profileForm.value.bio = (userStore.userInfo as any).bio || ''
      
      if (userStore.userInfo.avatar_url) {
        avatarUrl.value = userStore.userInfo.avatar_url
      }
    }
  }
}

// 触发头像上传
function triggerUpload() {
  avatarInput.value?.click()
}

// 处理头像选择
async function handleAvatarChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // 检查文件大小 (2MB)
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 2MB')
    return
  }
  
  // 检查文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('仅支持 JPG、PNG、GIF、WebP 格式的图片')
    return
  }
  
  avatarUploading.value = true
  
  try {
    const response = await authAPI.uploadAvatar(file) as any
    
    if (response.data?.avatar_url) {
      avatarUrl.value = response.data.avatar_url
      
      // 更新 store 中的用户信息
      if (userStore.userInfo) {
        userStore.userInfo.avatar_url = response.data.avatar_url
      }
      
      ElMessage.success('头像上传成功')
    } else {
      ElMessage.error(response.message || '头像上传失败')
    }
  } catch (error: any) {
    console.error('头像上传失败:', error)
    ElMessage.error(error.response?.data?.message || '头像上传失败')
  } finally {
    avatarUploading.value = false
    // 重置 input，允许再次选择相同文件
    target.value = ''
  }
}

// 加载统计数据
async function loadStats() {
  try {
    const res = await promptAPI.getList() as any
    const prompts = res.data || []
    
    stats.promptCount = prompts.length
    stats.favoriteCount = prompts.filter((p: any) => p.is_favorite).length
    stats.publicCount = prompts.filter((p: any) => p.is_public).length
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

function formatDate(dateString: string) {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function resetForm() {
  profileForm.value.email = userStore.userInfo?.email || ''
  profileForm.value.nickname = userStore.userInfo?.nickname || ''
  profileForm.value.phone = userStore.userInfo?.phone || ''
  profileForm.value.company = userStore.userInfo?.company || ''
  profileForm.value.location = userStore.userInfo?.location || ''
  profileForm.value.website = userStore.userInfo?.website || ''
  profileForm.value.bio = userStore.userInfo?.bio || ''
  formRef.value?.clearValidate()
}

function goToSecurity() {
  router.push('/security')
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true

    try {
      const updateData: any = {
        email: profileForm.value.email,
        nickname: profileForm.value.nickname,
        phone: profileForm.value.phone,
        company: profileForm.value.company,
        location: profileForm.value.location,
        website: profileForm.value.website,
        bio: profileForm.value.bio
      }

      const response = await authAPI.updateProfile(updateData) as any
      
      // 更新本地用户信息
      if (response.code === 0 && response.data) {
        // 合并更新用户信息
        if (userStore.userInfo) {
          Object.assign(userStore.userInfo, response.data)
        }
        ElMessage.success('个人资料更新成功')
      } else {
        ElMessage.error(response.message || '更新失败')
      }
    } catch (error: any) {
      console.error('更新失败:', error)
      ElMessage.error(error.response?.data?.message || '更新失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, #f5f7fa 0%, #e8edf3 100%);
}

.content-container {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  overflow-y: auto;
  max-height: calc(100vh - 60px);
}

.content-container::-webkit-scrollbar {
  width: 8px;
}

.content-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.content-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.content-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 个人资料头部 */
.profile-header {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e8edf3;
}

.avatar-upload {
  position: relative;
  cursor: pointer;
}

.avatar-upload .user-avatar {
  background: #409eff;
  font-size: 2rem;
  font-weight: 600;
  color: white;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
  font-size: 0.75rem;
}

.avatar-upload:hover .avatar-overlay {
  opacity: 1;
}

.avatar-overlay .el-icon {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.user-avatar {
  background: #409eff;
  font-size: 2rem;
  font-weight: 600;
  color: white;
}

.user-info {
  flex: 1;
}

.username {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  color: #303133;
  font-weight: 600;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.join-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #909399;
  font-size: 0.9rem;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s;
  border: 1px solid #e8edf3;
}

.stat-card:hover {
  background: #f0f2f5;
  border-color: #d0d4d9;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  flex-shrink: 0;
}

.prompt-icon {
  background: #409eff;
}

.favorite-icon {
  background: #f56c6c;
}

.public-icon {
  background: #67c23a;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.85rem;
  color: #909399;
}

/* 卡片样式 */
.profile-card,
.security-card,
.info-card {
  margin-bottom: 1.5rem;
  border-radius: 8px;
}

.security-actions {
  padding: 1rem;
  text-align: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-icon {
  font-size: 1.25rem;
  color: #409eff;
}

.header-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #303133;
}

/* 表单样式 */
.profile-form {
  padding: 0.5rem 0;
}

.profile-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.profile-form :deep(.el-divider) {
  margin: 1.5rem 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-container {
    padding: 1rem;
  }

  .profile-header {
    padding: 1.5rem;
  }

  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }

  .username {
    font-size: 1.5rem;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .user-meta {
    justify-content: center;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>

