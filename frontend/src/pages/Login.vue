<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <div class="logo-container">
          <img src="/logo.svg" alt="AI Prompt Lab" class="login-logo" />
        </div>
        <h1 class="welcome-title">欢迎来到 AI Prompt Lab</h1>
        <p class="subtitle">测试、对比、优化您的提示词</p>
      </div>

      <el-card class="login-card">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="登录" name="login">
            <el-form
              ref="loginFormRef"
              :model="loginForm"
              :rules="loginRules"
              @submit.prevent="handleLogin"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="用户名"
                  size="large"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="密码"
                  size="large"
                  show-password
                  @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  :loading="loading"
                  @click="handleLogin"
                  class="w-full"
                >
                  登录
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <el-form
              ref="registerFormRef"
              :model="registerForm"
              :rules="registerRules"
              @submit.prevent="handleRegister"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="用户名"
                  size="large"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item prop="email">
                <el-input
                  v-model="registerForm.email"
                  placeholder="邮箱"
                  size="large"
                >
                  <template #prefix>
                    <el-icon><Message /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="密码"
                  size="large"
                  show-password
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="确认密码"
                  size="large"
                  show-password
                  @keyup.enter="handleRegister"
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  :loading="loading"
                  @click="handleRegister"
                  class="w-full"
                >
                  注册
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <div class="login-footer">
        <p class="text-sm text-gray-500">
          调试 · 管理 · 对比 · 分享 Prompt
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage, FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ]
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度至少为3位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

async function handleLogin() {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await userStore.login(loginForm.username, loginForm.password)
      ElMessage.success('登录成功')
      
      const redirect = route.query.redirect as string || '/prompts'
      router.push(redirect)
    } catch (error) {
      // 错误已在 API 层处理
    } finally {
      loading.value = false
    }
  })
}

async function handleRegister() {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await userStore.register(
        registerForm.username,
        registerForm.email,
        registerForm.password
      )
      ElMessage.success('注册成功')
      router.push('/prompts')
    } catch (error) {
      // 错误已在 API 层处理
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #4285f4 100%);
  position: relative;
  overflow: hidden;
}

/* 动态背景圆圈效果 */
.login-page::before {
  content: '';
  position: absolute;
  top: -10%;
  left: -10%;
  width: 40%;
  height: 40%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  animation: float1 8s ease-in-out infinite;
  z-index: 0;
}

.login-page::after {
  content: '';
  position: absolute;
  bottom: -15%;
  right: -10%;
  width: 50%;
  height: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float2 10s ease-in-out infinite;
  z-index: 0;
}

@keyframes float1 {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(30px, -30px) scale(1.1);
  }
}

@keyframes float2 {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-40px, 40px) scale(1.15);
  }
}

.login-container {
  width: 100%;
  max-width: 440px;
  padding: 2rem;
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo-container {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
  position: relative;
}

.logo-container::before {
  content: '';
  position: absolute;
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.login-logo {
  height: 120px;
  width: 120px;
  filter: drop-shadow(0 10px 25px rgba(0, 0, 0, 0.3));
  animation: float 3s ease-in-out infinite;
  position: relative;
  z-index: 1;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  25% {
    transform: translateY(-8px) rotate(2deg);
  }
  75% {
    transform: translateY(-8px) rotate(-2deg);
  }
}

.welcome-title {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  margin-bottom: 0.75rem;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 400;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-card {
  backdrop-filter: blur(30px);
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.3) inset;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  padding: 2rem;
}

.login-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 25px 70px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.4) inset;
}

.login-card :deep(.el-card__body) {
  padding: 0;
}

.login-card :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.login-card :deep(.el-tabs__item) {
  font-size: 1.1rem;
  font-weight: 600;
  color: #666;
  transition: all 0.3s ease;
}

.login-card :deep(.el-tabs__item:hover) {
  color: #4285f4;
}

.login-card :deep(.el-tabs__item.is-active) {
  color: #4285f4;
  font-weight: 700;
}

.login-card :deep(.el-tabs__active-bar) {
  height: 3px;
  background: #4285f4;
}

.login-card :deep(.el-form-item) {
  margin-bottom: 1.5rem;
}

.login-card :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(102, 126, 234, 0.1);
  padding: 12px 16px;
}

.login-card :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 16px rgba(66, 133, 244, 0.2);
  border-color: rgba(66, 133, 244, 0.3);
  transform: translateY(-2px);
}

.login-card :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 6px 20px rgba(66, 133, 244, 0.3);
  border-color: #4285f4;
  transform: translateY(-2px);
}

.login-card :deep(.el-input__inner) {
  font-size: 0.95rem;
}

.login-card :deep(.el-input__prefix) {
  font-size: 1.1rem;
  color: #4285f4;
}

.login-card :deep(.el-button--primary) {
  border-radius: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  font-size: 1rem;
  background: linear-gradient(135deg, #4285f4 0%, #0d47a1 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(66, 133, 244, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.login-card :deep(.el-button--primary::before) {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.login-card :deep(.el-button--primary:hover) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(66, 133, 244, 0.5);
}

.login-card :deep(.el-button--primary:hover::before) {
  left: 100%;
}

.login-card :deep(.el-button--primary:active) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(66, 133, 244, 0.4);
}

.login-footer {
  text-align: center;
  margin-top: 2rem;
  animation: fadeIn 1s ease-out 0.5s both;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.login-footer p {
  color: rgba(255, 255, 255, 0.95);
  font-size: 0.9rem;
  font-weight: 500;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  letter-spacing: 0.5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    max-width: 90%;
    padding: 1rem;
  }
  
  .welcome-title {
    font-size: 1.5rem;
  }
  
  .subtitle {
    font-size: 0.9rem;
  }
  
  .login-logo {
    height: 90px;
    width: 90px;
  }
  
  .login-card {
    padding: 1.5rem;
  }
}
</style>

