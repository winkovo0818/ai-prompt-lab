import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/prompts'
  },
  {
    path: '/prompts',
    name: 'PromptList',
    component: () => import('@/pages/PromptList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/editor/:id?',
    name: 'PromptEditor',
    component: () => import('@/pages/PromptEditor.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/compare',
    name: 'CompareTest',
    component: () => import('@/pages/CompareTest.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/templates',
    name: 'Templates',
    component: () => import('@/pages/Templates.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/security',
    name: 'Security',
    component: () => import('@/pages/Security.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/pages/admin/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/prompts',
    name: 'AdminPrompts',
    component: () => import('@/pages/admin/Prompts.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/site-settings',
    name: 'AdminSiteSettings',
    component: () => import('@/pages/admin/SiteSettings.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/templates',
    name: 'AdminTemplates',
    component: () => import('@/pages/admin/Templates.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/audit-logs',
    name: 'AdminAuditLogs',
    component: () => import('@/pages/admin/AuditLogs.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/security-config',
    name: 'AdminSecurityConfig',
    component: () => import('@/pages/admin/SecurityConfig.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/global-ai-config',
    name: 'AdminGlobalAIConfig',
    component: () => import('@/pages/admin/GlobalAIConfig.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth !== false
  const requiresAdmin = to.meta.requiresAdmin === true

  console.log('🛡️ 路由守卫:', {
    to: to.path,
    from: from.path,
    token: userStore.token ? '存在' : '不存在',
    userInfo: userStore.userInfo ? '存在' : '不存在',
    isLoggedIn: userStore.isLoggedIn,
    requiresAuth,
    requiresAdmin,
    userRole: userStore.userInfo?.role
  })

  if (requiresAuth && !userStore.isLoggedIn) {
    // 需要登录但未登录，跳转到登录页
    console.warn('⚠️ 需要登录但未登录，跳转到登录页')
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (requiresAdmin && userStore.userInfo?.role !== 'admin') {
    // 需要管理员权限但不是管理员
    console.warn('⚠️ 需要管理员权限')
    next({ name: 'PromptList' })
  } else if (to.name === 'Login' && userStore.isLoggedIn) {
    // 已登录访问登录页，跳转到首页
    console.log('✅ 已登录访问登录页，跳转到首页')
    next({ name: 'PromptList' })
  } else {
    console.log('✅ 通过路由守卫')
    next()
  }
})

export default router

