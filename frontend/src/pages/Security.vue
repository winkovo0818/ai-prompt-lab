<template>
  <div class="security-page h-screen bg-zinc-50 dark:bg-zinc-950 flex flex-col overflow-hidden">
    <Header />
    
    <main class="flex-1 overflow-y-auto py-12 px-6">
      <div class="max-w-[1000px] mx-auto">
        
        <!-- Page Header -->
        <div class="flex items-center justify-between mb-12">
          <div class="space-y-1">
            <h1 class="text-2xl font-black text-zinc-900 dark:text-white tracking-tight uppercase">安全中心 Security</h1>
            <p class="text-zinc-500 text-sm font-medium">管理您的身份验证凭据与账户安全策略</p>
          </div>
          <button @click="goBack" class="flex items-center space-x-2 text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors">
            <el-icon><ArrowLeft /></el-icon>
            <span class="text-[10px] font-black uppercase tracking-widest">返回空间</span>
          </button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-[1fr,350px] gap-12">
          
          <!-- Left: Password Reset Section -->
          <div class="space-y-8">
            <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-8 shadow-subtle relative overflow-hidden">
              <div class="absolute top-0 left-0 w-1 h-full bg-zinc-900 dark:bg-white"></div>
              
              <div class="flex items-center space-x-4 mb-10">
                <div class="w-12 h-12 rounded-xl bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center text-zinc-900 dark:text-white border border-zinc-100 dark:border-zinc-700">
                  <el-icon :size="20"><Lock /></el-icon>
                </div>
                <div>
                  <h2 class="text-md font-bold text-zinc-900 dark:text-white tracking-tight">重置访问密码</h2>
                  <p class="text-xs text-zinc-500 font-medium mt-0.5">建议定期更换密码以确保您的资产安全</p>
                </div>
              </div>

              <el-form 
                ref="formRef"
                :model="passwordForm" 
                :rules="formRules"
                label-position="top"
                class="studio-security-form"
              >
                <el-form-item label="当前密码 CURRENT PASSWORD" prop="currentPassword">
                  <el-input 
                    v-model="passwordForm.currentPassword" 
                    type="password" 
                    placeholder="请输入您正在使用的密码"
                    show-password
                    class="studio-input-minimal"
                  />
                </el-form-item>

                <div class="space-y-6 mt-6">
                  <el-form-item label="设置新密码 NEW PASSWORD" prop="newPassword">
                    <el-input 
                      v-model="passwordForm.newPassword" 
                      type="password" 
                      placeholder="设置一个高强度的密码"
                      show-password
                      class="studio-input-minimal"
                    />
                    
                    <!-- Password Strength Meter -->
                    <div class="mt-4 space-y-2" v-if="passwordForm.newPassword">
                      <div class="flex justify-between items-center px-0.5">
                        <span class="text-[9px] font-black uppercase tracking-widest text-zinc-400">密码强度评级</span>
                        <span class="text-[9px] font-black uppercase tracking-widest" :class="passwordStrength.colorClass">
                          {{ passwordStrength.text }}
                        </span>
                      </div>
                      <div class="h-1 w-full bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                        <div 
                          class="h-full transition-all duration-500" 
                          :class="passwordStrength.bgClass"
                          :style="{ width: passwordStrength.percent + '%' }"
                        ></div>
                      </div>
                    </div>
                  </el-form-item>

                  <el-form-item label="确认新密码 CONFIRM NEW PASSWORD" prop="confirmPassword">
                    <el-input 
                      v-model="passwordForm.confirmPassword" 
                      type="password" 
                      placeholder="请再次输入新密码"
                      show-password
                      class="studio-input-minimal"
                    />
                  </el-form-item>
                </div>

                <div class="flex items-center space-x-4 pt-8">
                  <el-button 
                    type="primary" 
                    @click="handleSubmit" 
                    :loading="loading"
                    class="h-11 px-10 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-bold border-none shadow-premium hover:opacity-90"
                  >
                    更新密码
                  </el-button>
                  <el-button @click="resetForm" class="h-11 px-6 rounded-lg border-zinc-200 dark:border-zinc-800 font-bold text-zinc-500">清除重置</el-button>
                </div>
              </el-form>
            </div>
          </div>

          <!-- Right: Status & Tips -->
          <div class="space-y-6">
            <!-- Status Overview -->
            <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-subtle space-y-6">
              <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">账户完整度 Integrity</h3>
              
              <div class="space-y-4">
                <div class="flex items-center justify-between p-3 rounded-xl bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-700/50">
                  <div class="flex items-center space-x-3">
                    <el-icon class="text-emerald-500"><CircleCheckFilled /></el-icon>
                    <span class="text-xs font-bold text-zinc-700 dark:text-zinc-300">登录密码</span>
                  </div>
                  <span class="text-[10px] font-black uppercase tracking-widest text-emerald-600">已启用</span>
                </div>

                <div class="flex items-center justify-between p-3 rounded-xl bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-700/50">
                  <div class="flex items-center space-x-3">
                    <el-icon class="text-emerald-500"><CircleCheckFilled /></el-icon>
                    <span class="text-xs font-bold text-zinc-700 dark:text-zinc-300">邮箱关联</span>
                  </div>
                  <span class="text-[10px] font-black uppercase tracking-widest text-zinc-400">{{ userStore.userInfo?.email ? '已验证' : '未设置' }}</span>
                </div>

                <div class="p-3">
                  <p class="text-[10px] font-bold text-zinc-400 uppercase tracking-widest mb-1">最后一次安全登录</p>
                  <p class="text-xs font-mono font-bold text-zinc-900 dark:text-zinc-100">{{ formatDate(userStore.userInfo?.last_login_at) }}</p>
                </div>
              </div>
            </div>

            <!-- Security Notice -->
            <div class="p-6 border border-zinc-200 dark:border-zinc-800 rounded-2xl space-y-4">
              <div class="flex items-center space-x-2 text-zinc-900 dark:text-white">
                <el-icon :size="16"><InfoFilled /></el-icon>
                <span class="text-[10px] font-black uppercase tracking-widest">安全准则 Notice</span>
              </div>
              <ul class="space-y-3 px-1">
                <li v-for="tip in securityTips" :key="tip" class="flex items-start space-x-2">
                  <div class="w-1 h-1 rounded-full bg-zinc-300 mt-1.5 shrink-0"></div>
                  <span class="text-[11px] leading-relaxed text-zinc-500 font-medium">{{ tip }}</span>
                </li>
              </ul>
            </div>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { authAPI } from '@/api'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { Lock, ArrowLeft, CircleCheckFilled, InfoFilled } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const passwordForm = ref({ currentPassword: '', newPassword: '', confirmPassword: '' })

const securityTips = [
  '密码长度至少包含 8 个字符，建议使用大小写字母、数字及特殊符号组合。',
  '请勿在不同平台重复使用相同的密码。',
  '定期更新您的访问凭据，建议每 90 天更换一次。',
  '如果您怀疑账户存在异常访问，请立即联系系统管理员或重置密码。'
]

const passwordStrength = computed(() => {
  const pwd = passwordForm.value.newPassword
  if (!pwd) return { text: '', percent: 0, bgClass: '', colorClass: '' }
  let score = 0
  if (pwd.length >= 8) score += 1
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score += 1
  if (/\d/.test(pwd)) score += 1
  if (/[!@#$%^&*()]/.test(pwd)) score += 1
  
  if (score <= 1) return { text: '弱 Weak', percent: 25, bgClass: 'bg-rose-500', colorClass: 'text-rose-500' }
  if (score === 2) return { text: '中等 Medium', percent: 50, bgClass: 'bg-amber-500', colorClass: 'text-amber-500' }
  if (score === 3) return { text: '强 Strong', percent: 75, bgClass: 'bg-emerald-500', colorClass: 'text-emerald-500' }
  return { text: '极高 Premium', percent: 100, bgClass: 'bg-zinc-900 dark:bg-white', colorClass: 'text-zinc-900 dark:text-white' }
})

const formRules: FormRules = {
  currentPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '长度不能少于 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: (rule, val, callback) => val !== passwordForm.value.newPassword ? callback(new Error('两次输入不一致')) : callback(), trigger: 'blur' }
  ]
}

function formatDate(date: string | undefined) {
  if (!date) return '未知'
  const d = new Date(date)
  return `${d.getFullYear()}-${d.getMonth()+1}-${d.getDate()} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`
}

const goBack = () => router.back()
const resetForm = () => { passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' }; formRef.value?.clearValidate() }

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await authAPI.updateProfile({ password: passwordForm.value.newPassword })
      ElMessage.success('安全凭据更新成功，请重新登录')
      setTimeout(() => { userStore.logout(); router.push('/login') }, 2000)
    } finally { loading.value = false }
  })
}
</script>

<style scoped>
.studio-security-form :deep(.el-form-item__label) {
  @apply text-[10px] font-black uppercase tracking-widest text-zinc-400 mb-1.5 ml-0.5;
}

.studio-input-minimal :deep(.el-input__wrapper) {
  @apply bg-transparent !shadow-none border border-zinc-200 dark:border-zinc-800 rounded-lg h-11 px-4 transition-all hover:border-zinc-400 focus:border-zinc-900 dark:focus:border-zinc-100;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
