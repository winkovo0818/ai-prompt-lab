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
    path: '/repo/:id',
    name: 'PromptRepo',
    component: () => import('@/pages/PromptRepo.vue'),
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
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/pages/Statistics.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/teams',
    name: 'Teams',
    component: () => import('@/pages/Teams.vue'),
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
  },
  {
    path: '/admin/teams',
    name: 'AdminTeams',
    component: () => import('@/pages/admin/Teams.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quota',
    name: 'AdminQuota',
    component: () => import('@/pages/admin/QuotaManage.vue'),
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

  if (requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (requiresAdmin && userStore.userInfo?.role !== 'admin') {
    next({ name: 'PromptList' })
  } else if (to.name === 'Login' && userStore.isLoggedIn) {
    next({ name: 'PromptList' })
  } else {
    next()
  }
})

export default router

