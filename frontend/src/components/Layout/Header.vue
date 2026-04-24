<template>
  <header class="header-container glass-effect sticky top-0 z-[100] h-14 md:h-16 flex items-center justify-between px-4 md:px-8 border-b border-zinc-200 dark:border-zinc-800">
    <!-- Left Section: Logo & Nav -->
    <div class="flex items-center space-x-10">
      <router-link to="/prompts" class="logo-link flex items-center space-x-2.5 group">
        <div class="logo-icon-bg w-8 h-8 rounded-lg bg-zinc-900 dark:bg-white flex items-center justify-center transition-all group-hover:scale-105 group-hover:rotate-1 shadow-sm">
          <img src="/favicon.svg" alt="APL" class="w-5 h-5 invert dark:invert-0" />
        </div>
        <div class="flex flex-col">
          <span class="text-sm font-bold tracking-tight text-zinc-900 dark:text-zinc-100 hidden md:block leading-none uppercase">
            Prompt Lab
          </span>
          <span class="text-[9px] font-medium text-zinc-400 tracking-wider hidden md:block mt-0.5 uppercase">Professional Studio</span>
        </div>
      </router-link>

      <!-- Desktop Navigation -->
      <nav class="hidden lg:flex items-center space-x-1">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all"
          :class="isActive(item.path) ? 'text-zinc-900 dark:text-white bg-zinc-100 dark:bg-zinc-800/50' : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-zinc-800/30'"
        >
          <div class="flex items-center space-x-2">
            <el-icon :size="14"><component :is="item.icon" /></el-icon>
            <span>{{ item.name }}</span>
          </div>
        </router-link>

        <!-- Admin Dropdown -->
        <el-dropdown v-if="userStore.userInfo?.role === 'admin'" trigger="hover" class="ml-1">
          <div 
            class="nav-link px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider cursor-pointer transition-all duration-200"
            :class="isAdminActive() ? 'text-zinc-900 dark:text-white bg-zinc-100 dark:bg-zinc-800/50' : 'text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50 dark:hover:bg-zinc-800/30'"
          >
            <div class="flex items-center space-x-1">
              <el-icon :size="14"><Tools /></el-icon>
              <span>管理</span>
              <el-icon :size="10" class="ml-0.5 opacity-50"><ArrowDown /></el-icon>
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="admin-menu">
              <el-dropdown-item v-for="adminItem in adminItems" :key="adminItem.path" @click="router.push(adminItem.path)">
                <el-icon :size="14"><component :is="adminItem.icon" /></el-icon>
                <span class="text-xs font-medium">{{ adminItem.name }}</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </nav>
    </div>

    <!-- Right Section: User & Actions -->
    <div class="flex items-center space-x-4">
      <!-- User Profile -->
      <el-dropdown trigger="click">
        <div class="flex items-center space-x-2.5 p-1 px-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800/80 cursor-pointer transition-all border border-transparent hover:border-zinc-200 dark:hover:border-zinc-700">
          <el-avatar 
            :size="24" 
            :src="userStore.userInfo?.avatar_url"
            class="user-avatar shadow-sm ring-1 ring-zinc-200 dark:ring-zinc-700"
          >
            <el-icon v-if="!userStore.userInfo?.avatar_url" :size="12" class="text-zinc-500"><User /></el-icon>
          </el-avatar>
          <div class="hidden md:flex flex-col items-start leading-tight">
            <span class="text-xs font-semibold text-zinc-900 dark:text-zinc-100">{{ userStore.userInfo?.username }}</span>
          </div>
          <el-icon :size="10" class="opacity-30"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu class="user-menu">
            <el-dropdown-item @click="router.push('/profile')">
              <el-icon><User /></el-icon> 个人资料
            </el-dropdown-item>
            <el-dropdown-item @click="router.push('/security')">
              <el-icon><Lock /></el-icon> 安全设置
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout" class="logout-item">
              <el-icon><SwitchButton /></el-icon> 退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- Mobile Menu Trigger -->
      <button class="lg:hidden w-8 h-8 rounded-lg flex items-center justify-center text-zinc-600 hover:bg-zinc-100" @click="mobileMenuVisible = true">
        <el-icon :size="24"><Menu /></el-icon>
      </button>
    </div>

    <!-- Mobile Navigation Drawer -->
    <el-drawer
      v-model="mobileMenuVisible"
      direction="ltr"
      size="280px"
      :show-close="false"
      class="mobile-nav-drawer"
    >
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded bg-zinc-900 flex items-center justify-center">
              <img src="/favicon.svg" alt="APL" class="w-5 h-5 brightness-0 invert" />
            </div>
            <span class="font-bold text-zinc-900">Prompt Lab</span>
          </div>
          <el-button circle @click="mobileMenuVisible = false">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </template>
      
      <div class="mobile-nav-content py-4 px-2">
        <div class="section-title px-4 text-[10px] font-bold text-zinc-400 uppercase tracking-wider mb-2">主菜单</div>
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="mobile-nav-link flex items-center space-x-3 px-4 py-3 rounded-xl transition-all"
          :class="isActive(item.path) ? 'bg-zinc-100 text-zinc-900 font-bold' : 'text-zinc-600 hover:bg-zinc-50'"
          @click="mobileMenuVisible = false"
        >
          <el-icon :size="20"><component :is="item.icon" /></el-icon>
          <span>{{ item.name }}</span>
        </router-link>

        <template v-if="userStore.userInfo?.role === 'admin'">
          <div class="section-title px-4 text-[10px] font-bold text-zinc-400 uppercase tracking-wider mt-6 mb-2">管理系统</div>
          <router-link 
            v-for="adminItem in adminItems" 
            :key="adminItem.path"
            :to="adminItem.path" 
            class="mobile-nav-link flex items-center space-x-3 px-4 py-3 rounded-xl transition-all text-zinc-500 hover:bg-zinc-50"
            @click="mobileMenuVisible = false"
          >
            <el-icon :size="18"><component :is="adminItem.icon" /></el-icon>
            <span>{{ adminItem.name }}</span>
          </router-link>
        </template>
      </div>
    </el-drawer>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const mobileMenuVisible = ref(false)

const navItems = [
  { name: '工作台', path: '/prompts', icon: 'Memo' },
  { name: '团队协作', path: '/teams', icon: 'UserFilled' },
  { name: '对比测试', path: '/compare', icon: 'Connection' },
  { name: '模板库', path: '/templates', icon: 'Collection' },
  { name: '统计', path: '/statistics', icon: 'Histogram' },
  { name: '设置', path: '/settings', icon: 'Setting' }
]

const adminItems = [
  { name: '用户管理', path: '/admin/users', icon: 'UserFilled' },
  { name: '内容管理', path: '/admin/prompts', icon: 'DocumentCopy' },
  { name: '模板管理', path: '/admin/templates', icon: 'Collection' },
  { name: '团队管理', path: '/admin/teams', icon: 'UserFilled' },
  { name: '配额审计', path: '/admin/quota', icon: 'Odometer' },
  { name: '安全配置', path: '/admin/security-config', icon: 'Lock' },
  { name: '站点设置', path: '/admin/site-settings', icon: 'Setting' }
]

function isActive(path: string) {
  if (path === '/prompts') return route.path === '/prompts' || route.path.startsWith('/editor')
  return route.path.startsWith(path)
}

function isAdminActive() {
  return route.path.startsWith('/admin')
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      customClass: 'carbon-message-box'
    })
    userStore.logout()
    router.push('/login')
    ElMessage.success('已安全退出')
  } catch {
    // Cancelled
  }
}
</script>

<style scoped>
.header-container {
  background: var(--bg-base);
}

.logo-icon-bg {
  /* No more brand gradient, use solid dark/white */
}

.user-avatar {
  background-color: var(--bg-sidebar);
}

:deep(.admin-menu), :deep(.user-menu) {
  border-radius: 12px;
  padding: 6px;
  border: 1px solid var(--border-color);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  background-color: var(--bg-card);
}

:deep(.el-dropdown-menu__item) {
  border-radius: 6px;
  margin-bottom: 2px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 500;
}

:deep(.el-dropdown-menu__item:last-child) {
  margin-bottom: 0;
}

:deep(.logout-item) {
  color: #f43f5e;
}

:deep(.logout-item:hover) {
  background-color: #fff1f2 !important;
  color: #e11d48 !important;
}

@media (max-width: 768px) {
  .logo-link span {
    font-size: 14px;
  }
}
</style>
