<template>
  <div class="header bg-white border-b border-gray-200 flex items-center justify-between px-6 h-16">
    <div class="flex items-center space-x-4">
      <router-link to="/prompts" class="logo-link">
        <img src="/logo-horizontal.svg" alt="AI Prompt Lab" class="logo" />
      </router-link>
      <nav class="flex space-x-1">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
          :class="isActive(item.path) 
            ? 'bg-blue-50 text-blue-600' 
            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
        >
          <el-icon class="mr-1"><component :is="item.icon" /></el-icon>
          {{ item.name }}
        </router-link>
        
        <!-- 网站管理下拉菜单（仅管理员可见） -->
        <el-dropdown v-if="userStore.userInfo?.role === 'admin'" trigger="hover" class="admin-dropdown">
          <div 
            class="px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer"
            :class="isAdminActive() 
              ? 'bg-blue-50 text-blue-600' 
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
          >
            <el-icon class="mr-1"><Tools /></el-icon>
            网站管理
            <el-icon class="ml-1"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/admin/users')">
                <el-icon><UserFilled /></el-icon>
                用户管理
              </el-dropdown-item>
              <el-dropdown-item @click="router.push('/admin/prompts')">
                <el-icon><DocumentCopy /></el-icon>
                Prompt管理
              </el-dropdown-item>
              <el-dropdown-item @click="router.push('/admin/templates')">
                <el-icon><Collection /></el-icon>
                模板库管理
              </el-dropdown-item>
              <el-dropdown-item @click="router.push('/admin/teams')">
                <el-icon><UserFilled /></el-icon>
                团队管理
              </el-dropdown-item>
          <el-dropdown-item divided @click="router.push('/admin/security-config')">
            <el-icon><Lock /></el-icon>
            安全管理
          </el-dropdown-item>
          <el-dropdown-item @click="router.push('/admin/site-settings')">
            <el-icon><Setting /></el-icon>
            网站设置
          </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </nav>
    </div>

    <div class="flex items-center space-x-4">
      <el-dropdown trigger="click">
        <div class="flex items-center cursor-pointer hover:bg-gray-50 px-3 py-2 rounded-md user-dropdown">
          <el-avatar 
            :size="32" 
            class="mr-2" 
            :src="userStore.userInfo?.avatar_url"
            style="background-color: #409eff;"
          >
            <el-icon v-if="!userStore.userInfo?.avatar_url" :size="18" style="color: white;"><User /></el-icon>
          </el-avatar>
          <span class="text-sm text-gray-700">{{ userStore.userInfo?.username || '用户' }}</span>
          <el-icon class="ml-2" :size="14"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleProfile">
              <el-icon><User /></el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const siteName = ref('AI Prompt Lab')

onMounted(async () => {
  await loadSiteSettings()
  
  // 监听网站设置更新事件
  window.addEventListener('site-settings-updated', (event: any) => {
    siteName.value = event.detail.siteName
    document.title = siteName.value
  })
})

async function loadSiteSettings() {
  try {
    const { siteAPI } = await import('@/api')
    const response = await siteAPI.getPublicSettings() as any
    if (response.data && response.data.siteName) {
      siteName.value = response.data.siteName
      document.title = siteName.value
    }
  } catch (error) {
    console.error('读取网站设置失败:', error)
    // 使用默认值
    siteName.value = 'AI Prompt Lab'
  }
}

const navItems = [
  { name: 'Prompt 列表', path: '/prompts', icon: 'List' },
  { name: '团队', path: '/teams', icon: 'UserFilled' },
  { name: 'A/B 测试', path: '/compare', icon: 'DataAnalysis' },
  { name: '模板库', path: '/templates', icon: 'Collection' },
  { name: '使用统计', path: '/statistics', icon: 'DataLine' },
  { name: 'API设置', path: '/settings', icon: 'Setting' }
]

function isActive(path: string) {
  return route.path.startsWith(path)
}

function isAdminActive() {
  return route.path.startsWith('/admin')
}

function handleProfile() {
  router.push('/profile')
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.logo-link:hover {
  opacity: 0.8;
}

.logo {
  height: 48px;
  width: auto;
}

.admin-dropdown {
  display: inline-flex;
  align-items: center;
}

.user-dropdown {
  transition: all 0.2s ease;
}

.user-dropdown:hover {
  background-color: #f5f7fa;
}

.user-dropdown :deep(.el-avatar) {
  border: 2px solid #e4e7ed;
}
</style>

