<template>
  <div class="login-page-container min-h-screen flex items-center justify-center bg-white dark:bg-zinc-950 p-6 relative overflow-hidden">
    <!-- Suble Grid Background -->
    <div class="absolute inset-0 z-0 opacity-[0.03] dark:opacity-[0.05] pointer-events-none">
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" stroke-width="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
    </div>

    <!-- Auth Card -->
    <div class="w-full max-w-[420px] z-10 animate-fade-in">
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-zinc-900 dark:bg-white mb-6 shadow-soft">
          <img src="/favicon.svg" alt="APL" class="w-6 h-6 invert dark:invert-0" />
        </div>
        <h1 class="text-2xl font-bold text-zinc-900 dark:text-white tracking-tight mb-2">
          {{ activeTab === 'login' ? '欢迎回来' : '创建开发者账号' }}
        </h1>
        <p class="text-zinc-500 text-sm">
          {{ activeTab === 'login' ? '输入您的凭据访问 Prompt 实验室' : '开启您的智能提示词工程之旅' }}
        </p>
      </div>

      <!-- Main Form -->
      <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-8 shadow-premium">
        <!-- Tab Switcher -->
        <div class="flex bg-zinc-100 dark:bg-zinc-800 rounded-lg p-1 mb-8">
          <button 
            v-for="tab in ['login', 'register']" 
            :key="tab"
            @click="activeTab = tab"
            class="flex-1 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-all"
            :class="activeTab === tab ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm' : 'text-zinc-400 hover:text-zinc-600'"
          >
            {{ tab === 'login' ? '登录' : '注册' }}
          </button>
        </div>

        <!-- Login Form -->
        <el-form
          v-if="activeTab === 'login'"
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-position="top"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="用户名" prop="username">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" class="studio-auth-input" />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input v-model="loginForm.password" type="password" show-password placeholder="请输入密码" class="studio-auth-input" @keyup.enter="handleLogin" />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="w-full h-11 rounded-lg font-bold bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-none shadow-sm mt-4"
          >
            登录系统
          </el-button>
        </el-form>

        <!-- Register Form -->
        <el-form
          v-else
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          label-position="top"
          @submit.prevent="handleRegister"
        >
          <el-form-item label="用户名" prop="username">
            <el-input v-model="registerForm.username" placeholder="建议使用英文或数字" class="studio-auth-input" />
          </el-form-item>

          <el-form-item label="电子邮箱" prop="email">
            <el-input v-model="registerForm.email" placeholder="name@example.com" class="studio-auth-input" />
          </el-form-item>

          <el-form-item label="设置密码" prop="password">
            <el-input v-model="registerForm.password" type="password" show-password placeholder="至少 6 位字符" class="studio-auth-input" />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            class="w-full h-11 rounded-lg font-bold bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-none shadow-sm mt-4"
          >
            创建账号
          </el-button>
        </el-form>
      </div>

      <div class="mt-8 text-center">
        <p class="text-zinc-400 text-[11px] font-medium leading-relaxed max-w-[280px] mx-auto">
          登录即代表您同意我们的 <a href="#" class="text-zinc-600 dark:text-zinc-300 underline underline-offset-2">服务条款</a> 和 <a href="#" class="text-zinc-600 dark:text-zinc-300 underline underline-offset-2">隐私政策</a>
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

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', email: '', password: '' })

const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '邮箱格式错误', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '至少 6 位', trigger: 'blur' }]
}

async function handleLogin() {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await userStore.login(loginForm.username, loginForm.password)
      ElMessage.success('欢迎回来')
      router.push((route.query.redirect as string) || '/prompts')
    } catch (e) {} finally { loading.value = false }
  })
}

async function handleRegister() {
  if (!registerFormRef.value) return
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await userStore.register(registerForm.username, registerForm.email, registerForm.password)
      ElMessage.success('注册成功')
      router.push('/prompts')
    } catch (e) {} finally { loading.value = false }
  })
}
</script>

<style scoped>
:deep(.studio-auth-input .el-input__wrapper) {
  @apply rounded-lg bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 !shadow-none py-2 transition-all;
}

.animate-fade-in { animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
