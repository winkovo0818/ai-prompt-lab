<template>
  <div class="profile-page h-screen bg-zinc-50 dark:bg-zinc-950 flex flex-col overflow-hidden">
    <Header />
    
    <main class="flex-1 overflow-y-auto py-12 px-6">
      <div class="max-w-[900px] mx-auto space-y-12">
        
        <!-- Profile Header: Avatar & Identity -->
        <section class="flex flex-col md:flex-row items-center md:items-end space-y-6 md:space-y-0 md:space-x-8 pb-10 border-b border-zinc-200 dark:border-zinc-800">
          <div class="relative group cursor-pointer" @click="triggerUpload">
            <el-avatar 
              :size="120" 
              class="ring-4 ring-white dark:ring-zinc-900 shadow-premium"
              :src="avatarUrl"
            >
              {{ userStore.userInfo?.username?.[0]?.toUpperCase() || 'U' }}
            </el-avatar>
            <div class="absolute inset-0 rounded-full bg-black/40 opacity-0 group-hover:opacity-100 flex flex-col items-center justify-center text-white transition-opacity duration-200">
              <el-icon :size="24"><Camera /></el-icon>
              <span class="text-[10px] font-bold uppercase tracking-widest mt-1">更换头像</span>
            </div>
            <input 
              ref="avatarInput"
              type="file" 
              accept="image/*"
              style="display: none"
              @change="handleAvatarChange"
            />
          </div>

          <div class="flex-1 text-center md:text-left space-y-2">
            <div class="flex flex-col md:flex-row items-center md:items-end space-y-2 md:space-y-0 md:space-x-4">
              <h1 class="text-3xl font-black text-zinc-900 dark:text-white tracking-tight">
                {{ userStore.userInfo?.username }}
              </h1>
              <div class="flex items-center space-x-2 pb-1.5">
                <span class="px-2 py-0.5 rounded bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 text-[9px] font-black uppercase tracking-widest">
                  {{ userStore.userInfo?.role === 'admin' ? 'Administrator' : 'Developer' }}
                </span>
                <span v-if="userStore.userInfo?.is_active" class="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 text-[9px] font-black uppercase tracking-widest">
                  <div class="w-1 h-1 rounded-full bg-current"></div>
                  <span>Active</span>
                </span>
              </div>
            </div>
            <p class="text-zinc-500 dark:text-zinc-400 text-sm font-medium">
              注册于 {{ formatDate(userStore.userInfo?.created_at, 'YYYY年MM月DD日') }} · 累计登录 {{ userStore.userInfo?.login_count || 0 }} 次
            </p>
          </div>

          <!-- Quick Stats Row -->
          <div class="grid grid-cols-3 gap-8 md:gap-12 shrink-0">
            <div class="flex flex-col items-center md:items-start">
              <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.2em]">Prompts</span>
              <span class="text-xl font-bold text-zinc-900 dark:text-white">{{ stats.promptCount }}</span>
            </div>
            <div class="flex flex-col items-center md:items-start">
              <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.2em]">Stars</span>
              <span class="text-xl font-bold text-zinc-900 dark:text-white">{{ stats.favoriteCount }}</span>
            </div>
            <div class="flex flex-col items-center md:items-start">
              <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.2em]">Public</span>
              <span class="text-xl font-bold text-zinc-900 dark:text-white">{{ stats.publicCount }}</span>
            </div>
          </div>
        </section>

        <!-- Main Form Content -->
        <div class="grid grid-cols-1 lg:grid-cols-[1fr,300px] gap-12">
          
          <!-- Edit Form Container -->
          <div class="space-y-10">
            <section class="space-y-6">
              <div class="flex items-center space-x-2 mb-2">
                <div class="w-1 h-4 bg-zinc-900 dark:bg-white rounded-full"></div>
                <h2 class="text-xs font-black uppercase tracking-widest text-zinc-900 dark:text-white">基本信息 Setting</h2>
              </div>

              <el-form 
                ref="formRef"
                :model="profileForm" 
                :rules="formRules"
                label-position="top"
                class="studio-form-compact"
              >
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <el-form-item label="公开昵称 Display Name" prop="nickname">
                    <el-input v-model="profileForm.nickname" placeholder="如何称呼您" class="studio-input-minimal" />
                  </el-form-item>
                  <el-form-item label="电子邮箱 Email" prop="email">
                    <el-input v-model="profileForm.email" placeholder="name@example.com" class="studio-input-minimal" />
                  </el-form-item>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                  <el-form-item label="联系电话 Phone" prop="phone">
                    <el-input v-model="profileForm.phone" placeholder="您的联系电话" class="studio-input-minimal" />
                  </el-form-item>
                  <el-form-item label="所在地 Location" prop="location">
                    <el-input v-model="profileForm.location" placeholder="城市, 国家" class="studio-input-minimal" />
                  </el-form-item>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                  <el-form-item label="公司/组织 Organization" prop="company">
                    <el-input v-model="profileForm.company" placeholder="您就职的单位" class="studio-input-minimal" />
                  </el-form-item>
                  <el-form-item label="个人主页 Website" prop="website">
                    <el-input v-model="profileForm.website" placeholder="https://" class="studio-input-minimal" />
                  </el-form-item>
                </div>

                <el-form-item label="个人简介 Biography" prop="bio" class="mt-4">
                  <el-input 
                    v-model="profileForm.bio" 
                    type="textarea"
                    :rows="4"
                    placeholder="简单的描述一下您的专业背景或兴趣爱好..."
                    maxlength="500"
                    show-word-limit
                    class="studio-textarea-minimal"
                  />
                </el-form-item>

                <div class="flex items-center space-x-4 pt-6">
                  <el-button 
                    type="primary" 
                    @click="handleSubmit" 
                    :loading="loading"
                    class="h-10 px-8 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-bold border-none shadow-premium hover:opacity-90"
                  >
                    保存更新
                  </el-button>
                  <el-button @click="resetForm" class="h-10 px-6 rounded-lg border-zinc-200 dark:border-zinc-800 font-bold text-zinc-500">重置</el-button>
                </div>
              </el-form>
            </section>
          </div>

          <!-- Sidebar Info -->
          <div class="space-y-8">
            <!-- Account Info Card -->
            <div class="p-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-subtle space-y-6">
              <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">账户状态 Security</h3>
              
              <div class="space-y-4">
                <div class="flex justify-between items-center text-xs">
                  <span class="text-zinc-500 font-medium">账户 ID</span>
                  <span class="font-mono text-zinc-900 dark:text-zinc-100 font-bold">#{{ userStore.userInfo?.id }}</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-zinc-500 font-medium">最后活跃</span>
                  <span class="text-zinc-900 dark:text-zinc-100 font-bold">{{ formatDate(userStore.userInfo?.updated_at, 'MM-DD HH:mm') }}</span>
                </div>
              </div>

              <div class="pt-4 border-t border-zinc-100 dark:border-zinc-800">
                <el-button @click="goToSecurity" class="w-full justify-between h-10 rounded-xl border-zinc-200 dark:border-zinc-800 group transition-all hover:bg-zinc-50 dark:hover:bg-zinc-800">
                  <div class="flex items-center">
                    <el-icon class="mr-2 text-zinc-400 group-hover:text-zinc-900 dark:group-hover:text-white"><Lock /></el-icon>
                    <span class="text-xs font-bold text-zinc-600 dark:text-zinc-400 group-hover:text-zinc-900 dark:group-hover:text-white">修改安全密码</span>
                  </div>
                  <el-icon :size="12" class="text-zinc-300 group-hover:translate-x-1 transition-transform"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- Pro Tip -->
            <div class="p-5 bg-zinc-900 dark:bg-zinc-100 rounded-2xl shadow-premium">
              <div class="flex items-center space-x-2 text-brand-accent mb-2">
                <el-icon :size="16"><MagicStick /></el-icon>
                <span class="text-[10px] font-black uppercase tracking-widest">Studio Tip</span>
              </div>
              <p class="text-zinc-400 dark:text-zinc-500 text-[11px] leading-relaxed font-medium">
                完善您的个人资料可以帮助团队成员在协作时更准确地识别您的提交。
              </p>
            </div>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { authAPI, promptAPI } from '@/api'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { 
  User, Lock, Camera, ArrowRight, MagicStick
} from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const avatarInput = ref<HTMLInputElement>()

const avatarUrl = ref('')
const avatarUploading = ref(false)
const loading = ref(false)

const profileForm = ref({
  email: '',
  nickname: '',
  phone: '',
  company: '',
  location: '',
  website: '',
  bio: ''
})

const stats = reactive({ promptCount: 0, favoriteCount: 0, publicCount: 0 })

const formRules: FormRules = {
  email: [
    { required: true, message: '邮箱不能为空', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

onMounted(async () => {
  await loadUserInfo()
  await loadStats()
})

async function loadUserInfo() {
  try {
    const response = await authAPI.getCurrentUser() as any
    if (response.data) {
      Object.assign(userStore.userInfo || {}, response.data)
      profileForm.value = {
        email: response.data.email || '',
        nickname: response.data.nickname || '',
        phone: response.data.phone || '',
        company: response.data.company || '',
        location: response.data.location || '',
        website: response.data.website || '',
        bio: response.data.bio || ''
      }
      if (response.data.avatar_url) avatarUrl.value = response.data.avatar_url
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

function triggerUpload() { avatarInput.value?.click() }

async function handleAvatarChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) { ElMessage.error('图片大小不能超过 2MB'); return }
  avatarUploading.value = true
  try {
    const response = await authAPI.uploadAvatar(file) as any
    if (response.data?.avatar_url) {
      avatarUrl.value = response.data.avatar_url
      if (userStore.userInfo) userStore.userInfo.avatar_url = response.data.avatar_url
      ElMessage.success('头像上传成功')
    }
  } finally {
    avatarUploading.value = false
    target.value = ''
  }
}

async function loadStats() {
  try {
    const res = await promptAPI.getList() as any
    const prompts = res.data?.items || []
    stats.promptCount = prompts.length
    stats.favoriteCount = prompts.filter((p: any) => p.is_favorite).length
    stats.publicCount = prompts.filter((p: any) => p.is_public).length
  } catch (error) { console.error('加载统计失败:', error) }
}

function formatDate(dateString: string | undefined, formatStr: string) {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return formatStr === 'YYYY年MM月DD日' 
    ? `${date.getFullYear()}年${date.getMonth()+1}月${date.getDate()}日`
    : `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${date.getMinutes()}`
}

function resetForm() {
  if (userStore.userInfo) {
    profileForm.value = {
      email: userStore.userInfo.email || '',
      nickname: (userStore.userInfo as any).nickname || '',
      phone: (userStore.userInfo as any).phone || '',
      company: (userStore.userInfo as any).company || '',
      location: (userStore.userInfo as any).location || '',
      website: (userStore.userInfo as any).website || '',
      bio: (userStore.userInfo as any).bio || ''
    }
  }
  formRef.value?.clearValidate()
}

function goToSecurity() { router.push('/security') }

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const response = await authAPI.updateProfile(profileForm.value) as any
      if (response.data) {
        Object.assign(userStore.userInfo!, response.data)
        ElMessage.success('资料已同步更新')
      }
    } finally { loading.value = false }
  })
}
</script>

<style scoped>
.studio-form-compact :deep(.el-form-item__label) {
  @apply text-[10px] font-black uppercase tracking-widest text-zinc-400 mb-1.5 ml-0.5;
}

.studio-input-minimal :deep(.el-input__wrapper) {
  @apply bg-transparent !shadow-none border border-zinc-200 dark:border-zinc-800 rounded-lg h-10 px-3 transition-all hover:border-zinc-400 focus:border-zinc-900 dark:focus:border-zinc-100;
}

.studio-textarea-minimal :deep(.el-textarea__inner) {
  @apply bg-transparent !shadow-none border border-zinc-200 dark:border-zinc-800 rounded-lg p-3 transition-all hover:border-zinc-400 focus:border-zinc-900 dark:focus:border-zinc-100 text-sm leading-relaxed;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
