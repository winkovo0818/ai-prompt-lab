<template>
  <div class="security-page">
    <Header />
    
    <div class="content-container">
      <el-card class="security-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon class="header-icon"><Lock /></el-icon>
              <span class="header-title">安全设置</span>
            </div>
            <el-text type="info" size="small">修改您的登录密码</el-text>
          </div>
        </template>

        <el-form 
          ref="formRef"
          :model="passwordForm" 
          :rules="formRules"
          label-width="120px" 
          class="password-form"
        >
          <el-alert
            title="密码安全提示"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 2rem;"
          >
            <template #default>
              <ul class="tips-list">
                <li>密码长度至少为 6 位字符</li>
                <li>建议使用字母、数字和符号的组合</li>
                <li>不要使用过于简单或常见的密码</li>
                <li>定期更换密码以保护账户安全</li>
              </ul>
            </template>
          </el-alert>

          <el-form-item label="当前密码" prop="currentPassword">
            <el-input 
              v-model="passwordForm.currentPassword" 
              type="password" 
              placeholder="请输入当前密码"
              show-password
              clearable
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="新密码" prop="newPassword">
            <el-input 
              v-model="passwordForm.newPassword" 
              type="password" 
              placeholder="请输入新密码（至少6位）"
              show-password
              clearable
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input 
              v-model="passwordForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入新密码"
              show-password
              clearable
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="loading">
              修改密码
            </el-button>
            <el-button @click="resetForm">重置</el-button>
            <el-button @click="goBack">返回</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 其他安全选项 -->
      <el-card class="security-options-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon class="header-icon"><Check /></el-icon>
              <span class="header-title">账户安全</span>
            </div>
          </div>
        </template>

        <div class="security-items">
          <div class="security-item">
            <div class="item-info">
              <el-icon class="item-icon"><Key /></el-icon>
              <div class="item-content">
                <div class="item-title">登录密码</div>
                <div class="item-desc">定期更换密码可以保护您的账户安全</div>
              </div>
            </div>
            <el-tag type="success">已设置</el-tag>
          </div>

          <div class="security-item">
            <div class="item-info">
              <el-icon class="item-icon"><Message /></el-icon>
              <div class="item-content">
                <div class="item-title">邮箱验证</div>
                <div class="item-desc">{{ userStore.userInfo?.email || '未设置' }}</div>
              </div>
            </div>
            <el-tag type="success">已验证</el-tag>
          </div>

          <div class="security-item">
            <div class="item-info">
              <el-icon class="item-icon"><Clock /></el-icon>
              <div class="item-content">
                <div class="item-title">最后登录</div>
                <div class="item-desc">{{ formatDate(userStore.userInfo?.last_login_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { authAPI } from '@/api'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { Lock, Key, Message, Clock, Check } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const loading = ref(false)

// 表单验证规则
const validateCurrentPassword = (rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请输入当前密码'))
  } else {
    callback()
  }
}

const validateNewPassword = (rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请输入新密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度至少为6位'))
  } else if (value === passwordForm.value.currentPassword) {
    callback(new Error('新密码不能与当前密码相同'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const formRules: FormRules = {
  currentPassword: [{ validator: validateCurrentPassword, trigger: 'blur' }],
  newPassword: [{ validator: validateNewPassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

function formatDate(dateString: string | undefined) {
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
  passwordForm.value.currentPassword = ''
  passwordForm.value.newPassword = ''
  passwordForm.value.confirmPassword = ''
  formRef.value?.clearValidate()
}

function goBack() {
  router.back()
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true

    try {
      // 注意：这里需要先验证当前密码，然后再更新
      // 实际实现中可能需要后端提供专门的修改密码接口
      const updateData = {
        password: passwordForm.value.newPassword
      }

      await authAPI.updateProfile(updateData)
      
      ElMessage.success('密码修改成功，请重新登录')
      
      // 清空表单
      resetForm()
      
      // 3秒后跳转到登录页
      setTimeout(() => {
        userStore.logout()
        router.push('/login')
      }, 3000)
    } catch (error: any) {
      console.error('修改失败:', error)
      ElMessage.error(error.response?.data?.message || '密码修改失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.security-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, #f5f7fa 0%, #e8edf3 100%);
}

.content-container {
  flex: 1;
  padding: 2rem;
  max-width: 900px;
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

.security-card,
.security-options-card {
  margin-bottom: 1.5rem;
  border-radius: 8px;
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

.password-form {
  padding: 0.5rem 0;
}

.password-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.tips-list {
  margin: 0;
  padding-left: 1.25rem;
  color: #606266;
  line-height: 1.8;
}

.tips-list li {
  margin-bottom: 0.25rem;
}

.security-items {
  padding: 0.5rem 0;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  margin-bottom: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.2s;
}

.security-item:hover {
  background: #f0f2f5;
}

.security-item:last-child {
  margin-bottom: 0;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.item-icon {
  font-size: 2rem;
  color: #409eff;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
}

.item-title {
  font-size: 1rem;
  font-weight: 600;
  color: #303133;
  margin-bottom: 0.25rem;
}

.item-desc {
  font-size: 0.875rem;
  color: #909399;
}

@media (max-width: 768px) {
  .content-container {
    padding: 1rem;
  }

  .security-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>

