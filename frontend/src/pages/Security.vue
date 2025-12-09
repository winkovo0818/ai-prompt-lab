<template>
  <div class="security-page">
    <Header />
    
    <div class="page-content">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="header-info">
          <h1 class="page-title">安全设置</h1>
          <p class="page-desc">管理您的账户安全和密码</p>
        </div>
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>

      <div class="content-grid">
        <!-- 左侧：修改密码 -->
        <div class="main-section">
          <div class="section-card">
            <div class="section-header">
              <div class="section-icon">
                <el-icon><Lock /></el-icon>
              </div>
              <div class="section-info">
                <h2 class="section-title">修改密码</h2>
                <p class="section-desc">定期更换密码可以保护您的账户安全</p>
              </div>
            </div>

            <el-form 
              ref="formRef"
              :model="passwordForm" 
              :rules="formRules"
              label-position="top"
              class="password-form"
            >
              <el-form-item label="当前密码" prop="currentPassword">
                <el-input 
                  v-model="passwordForm.currentPassword" 
                  type="password" 
                  placeholder="请输入当前密码"
                  show-password
                  size="large"
                />
              </el-form-item>

              <el-form-item label="新密码" prop="newPassword">
                <el-input 
                  v-model="passwordForm.newPassword" 
                  type="password" 
                  placeholder="请输入新密码（至少6位）"
                  show-password
                  size="large"
                />
                <div class="password-strength" v-if="passwordForm.newPassword">
                  <div class="strength-bar">
                    <div 
                      class="strength-fill" 
                      :class="passwordStrength.level"
                      :style="{ width: passwordStrength.percent + '%' }"
                    ></div>
                  </div>
                  <span class="strength-text" :class="passwordStrength.level">
                    {{ passwordStrength.text }}
                  </span>
                </div>
              </el-form-item>

              <el-form-item label="确认新密码" prop="confirmPassword">
                <el-input 
                  v-model="passwordForm.confirmPassword" 
                  type="password" 
                  placeholder="请再次输入新密码"
                  show-password
                  size="large"
                />
              </el-form-item>

              <div class="form-actions">
                <el-button 
                  type="primary" 
                  size="large"
                  @click="handleSubmit" 
                  :loading="loading"
                >
                  确认修改
                </el-button>
                <el-button size="large" @click="resetForm">重置</el-button>
              </div>
            </el-form>
          </div>
        </div>

        <!-- 右侧：安全状态 -->
        <div class="side-section">
          <div class="section-card">
            <h3 class="side-title">账户安全状态</h3>
            
            <div class="status-list">
              <div class="status-item">
                <div class="status-icon success">
                  <el-icon><CircleCheckFilled /></el-icon>
                </div>
                <div class="status-info">
                  <div class="status-label">登录密码</div>
                  <div class="status-value">已设置</div>
                </div>
              </div>

              <div class="status-item">
                <div class="status-icon success">
                  <el-icon><CircleCheckFilled /></el-icon>
                </div>
                <div class="status-info">
                  <div class="status-label">邮箱验证</div>
                  <div class="status-value">{{ userStore.userInfo?.email || '未设置' }}</div>
                </div>
              </div>

              <div class="status-item">
                <div class="status-icon info">
                  <el-icon><Clock /></el-icon>
                </div>
                <div class="status-info">
                  <div class="status-label">最后登录</div>
                  <div class="status-value">{{ formatDate(userStore.userInfo?.last_login_at) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 安全提示 -->
          <div class="tips-card">
            <div class="tips-header">
              <el-icon><InfoFilled /></el-icon>
              <span>安全提示</span>
            </div>
            <ul class="tips-list">
              <li>密码长度至少 6 位</li>
              <li>建议使用字母、数字组合</li>
              <li>避免使用常见密码</li>
              <li>定期更换密码</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { authAPI } from '@/api'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { Lock, Clock, ArrowLeft, CircleCheckFilled, InfoFilled } from '@element-plus/icons-vue'
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

// 密码强度计算
const passwordStrength = computed(() => {
  const pwd = passwordForm.value.newPassword
  if (!pwd) return { level: '', text: '', percent: 0 }
  
  let score = 0
  if (pwd.length >= 6) score += 1
  if (pwd.length >= 8) score += 1
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score += 1
  if (/\d/.test(pwd)) score += 1
  if (/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) score += 1
  
  if (score <= 2) return { level: 'weak', text: '弱', percent: 33 }
  if (score <= 3) return { level: 'medium', text: '中', percent: 66 }
  return { level: 'strong', text: '强', percent: 100 }
})

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
  background: #f5f7fa;
}

.page-content {
  flex: 1;
  padding: 24px 32px;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.page-desc {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
}

.section-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e5e7eb;
}

.section-header {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.section-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.section-desc {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* 表单 */
.password-form {
  max-width: 400px;
}

.password-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.password-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: none;
  border: 1px solid #d1d5db;
}

.password-form :deep(.el-input__wrapper:hover) {
  border-color: #9ca3af;
}

.password-form :deep(.el-input__wrapper.is-focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 密码强度 */
.password-strength {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s, background 0.3s;
}

.strength-fill.weak { background: #ef4444; }
.strength-fill.medium { background: #f59e0b; }
.strength-fill.strong { background: #10b981; }

.strength-text {
  font-size: 12px;
  font-weight: 500;
}

.strength-text.weak { color: #ef4444; }
.strength-text.medium { color: #f59e0b; }
.strength-text.strong { color: #10b981; }

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.form-actions :deep(.el-button--primary) {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border: none;
}

/* 右侧 */
.side-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.side-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.status-icon.success {
  background: #dcfce7;
  color: #16a34a;
}

.status-icon.info {
  background: #e0e7ff;
  color: #4f46e5;
}

.status-label {
  font-size: 13px;
  color: #6b7280;
}

.status-value {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

/* 提示卡片 */
.tips-card {
  background: #fefce8;
  border: 1px solid #fef08a;
  border-radius: 10px;
  padding: 16px;
}

.tips-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #854d0e;
  margin-bottom: 12px;
}

.tips-list {
  margin: 0;
  padding-left: 20px;
  color: #a16207;
  font-size: 13px;
  line-height: 1.8;
}

@media (max-width: 900px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .page-content {
    padding: 16px;
  }
}
</style>

