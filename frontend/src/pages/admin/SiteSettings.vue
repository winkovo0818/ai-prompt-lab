<template>
  <div class="site-settings-page">
    <Header />
    
    <div class="content">
      <el-card>
        <template #header>
          <h2>网站设置</h2>
        </template>

        <el-form :model="siteSettings" label-width="120px" class="settings-form">
          <el-divider content-position="left">基本信息</el-divider>
          
          <el-form-item label="网站名称">
            <el-input v-model="siteSettings.site_name" placeholder="AI Prompt Lab" />
          </el-form-item>

          <el-form-item label="网站描述">
            <el-input 
              v-model="siteSettings.site_description" 
              type="textarea" 
              :rows="3"
              placeholder="AI Prompt 智能工作台 - 调试、管理、对比、分享 Prompt"
            />
          </el-form-item>

          <el-form-item label="网站关键词">
            <el-input 
              v-model="siteSettings.site_keywords" 
              placeholder="AI, Prompt, 工作台"
            />
          </el-form-item>

          <el-divider content-position="left">显示设置</el-divider>

          <el-form-item label="每页显示数量">
            <el-input-number v-model="siteSettings.page_size" :min="10" :max="100" :step="10" />
            <span class="ml-2 text-sm text-gray-500">Prompt列表每页显示的数量</span>
          </el-form-item>

          <el-form-item label="允许用户注册">
            <el-switch v-model="siteSettings.allow_register" />
            <span class="ml-2 text-sm text-gray-500">关闭后新用户无法注册</span>
          </el-form-item>

          <el-form-item label="默认公开Prompt">
            <el-switch v-model="siteSettings.default_public" />
            <span class="ml-2 text-sm text-gray-500">新建Prompt时默认是否公开</span>
          </el-form-item>

          <el-divider content-position="left">功能设置</el-divider>

          <el-form-item label="启用A/B测试">
            <el-switch v-model="siteSettings.enable_abtest" />
            <span class="ml-2 text-sm text-gray-500">启用A/B测试功能</span>
          </el-form-item>

          <el-form-item label="最大测试Prompt数">
            <el-input-number v-model="siteSettings.max_abtest_prompts" :min="2" :max="10" />
            <span class="ml-2 text-sm text-gray-500">A/B测试最多可对比的Prompt数量</span>
          </el-form-item>

          <el-divider content-position="left">系统信息</el-divider>

          <el-form-item label="版本号">
            <el-input v-model="siteSettings.version" disabled />
          </el-form-item>

          <el-form-item label="最后更新">
            <el-input :value="formatDate(siteSettings.updated_at)" disabled />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveSettings" :loading="saving">
              保存设置
            </el-button>
            <el-button @click="resetSettings">
              恢复默认
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminAPI } from '@/api'
import Header from '@/components/Layout/Header.vue'

interface SiteSettings {
  id?: number
  site_name: string
  site_description: string
  site_keywords: string
  page_size: number
  allow_register: boolean
  default_public: boolean
  enable_abtest: boolean
  max_abtest_prompts: number
  version: string
  updated_at: string
}

const siteSettings = ref<SiteSettings>({
  site_name: 'AI Prompt Lab',
  site_description: 'AI Prompt 智能工作台 - 调试、管理、对比、分享 Prompt',
  site_keywords: 'AI, Prompt, 工作台',
  page_size: 20,
  allow_register: true,
  default_public: false,
  enable_abtest: true,
  max_abtest_prompts: 5,
  version: '1.0.0',
  updated_at: new Date().toISOString()
})

const saving = ref(false)
const loading = ref(false)

onMounted(() => {
  loadSettings()
})

async function loadSettings() {
  loading.value = true
  try {
    const response = await adminAPI.getSiteSettings() as any
    if (response.data) {
      siteSettings.value = response.data
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败')
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  
  try {
    const updateData = {
      site_name: siteSettings.value.site_name,
      site_description: siteSettings.value.site_description,
      site_keywords: siteSettings.value.site_keywords,
      page_size: siteSettings.value.page_size,
      allow_register: siteSettings.value.allow_register,
      default_public: siteSettings.value.default_public,
      enable_abtest: siteSettings.value.enable_abtest,
      max_abtest_prompts: siteSettings.value.max_abtest_prompts
    }
    
    const response = await adminAPI.updateSiteSettings(updateData) as any
    if (response.data) {
      siteSettings.value = response.data
    }
    
    // 更新document.title
    document.title = siteSettings.value.site_name
    
    // 触发自定义事件通知Header更新
    window.dispatchEvent(new CustomEvent('site-settings-updated', {
      detail: { siteName: siteSettings.value.site_name }
    }))
    
    ElMessage.success('设置保存成功')
  } catch (error: any) {
    console.error('保存设置失败:', error)
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function resetSettings() {
  ElMessageBox.confirm('确定要恢复默认设置吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    siteSettings.value = {
      site_name: 'AI Prompt Lab',
      site_description: 'AI Prompt 智能工作台 - 调试、管理、对比、分享 Prompt',
      site_keywords: 'AI, Prompt, 工作台',
      page_size: 20,
      allow_register: true,
      default_public: false,
      enable_abtest: true,
      max_abtest_prompts: 5,
      version: '1.0.0',
      updated_at: new Date().toISOString()
    }
    await saveSettings()
    ElMessage.success('已恢复默认设置')
  }).catch(() => {
    // 用户取消
  })
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.site-settings-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.content {
  flex: 1;
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

.settings-form {
  max-width: 800px;
}

.el-divider {
  margin: 2rem 0 1.5rem;
}

.el-divider:first-of-type {
  margin-top: 0;
}
</style>

