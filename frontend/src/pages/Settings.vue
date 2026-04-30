<template>
  <div class="settings-page h-screen bg-zinc-50 dark:bg-zinc-950 flex flex-col overflow-hidden">
    <Header />
    
    <main class="flex-1 overflow-y-auto py-12 px-6">
      <div class="max-w-[1200px] mx-auto space-y-12">
        
        <!-- Page Header -->
        <div class="flex items-center justify-between mb-8">
          <div class="space-y-1">
            <h1 class="text-2xl font-black text-zinc-900 dark:text-white tracking-tight uppercase">配置管理 AI Console</h1>
            <p class="text-zinc-500 text-sm font-medium">配置多端 AI 推理引擎，定义系统全局运行参数</p>
          </div>
          <el-button type="primary" @click="showAddDialog = true" class="h-10 px-6 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-bold border-none shadow-premium">
            <el-icon class="mr-2"><Plus /></el-icon>添加新引擎
          </el-button>
        </div>

        <!-- Section: Global Config (Admin Only) -->
        <section v-if="userStore.userInfo?.role === 'admin'" class="space-y-6">
          <div class="flex items-center justify-between px-1">
            <div class="flex items-center space-x-2">
              <div class="w-1 h-4 bg-zinc-900 dark:bg-white rounded-full"></div>
              <h2 class="text-xs font-black uppercase tracking-widest text-zinc-900 dark:text-white">系统预设 Global Defaults</h2>
            </div>
            <button @click="navigateToGlobalConfig" class="text-[10px] font-black uppercase tracking-widest text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors">
              管理核心路由
            </button>
          </div>
          
          <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-subtle flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            <div class="flex items-center space-x-6">
              <div class="w-12 h-12 rounded-2xl bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center text-zinc-400">
                <el-icon :size="24"><Setting /></el-icon>
              </div>
              <div>
                <div class="flex items-center space-x-2 mb-1">
                  <span class="text-sm font-bold text-zinc-900 dark:text-white">系统默认服务通道</span>
                  <span :class="globalAIConfig?.enable_default_ai ? 'bg-emerald-50 text-emerald-600' : 'bg-zinc-100 text-zinc-400'" class="px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest">
                    {{ globalAIConfig?.enable_default_ai ? 'Running' : 'Offline' }}
                  </span>
                </div>
                <p class="text-xs text-zinc-500 font-medium">
                  {{ globalAIConfig?.enable_default_ai ? `当前路由至: ${globalAIConfig.default_ai_model}` : '尚未启用全局默认 AI，用户需自行配置节点' }}
                </p>
              </div>
            </div>
            <div v-if="globalAIConfig?.enable_default_ai" class="flex items-center space-x-8 px-6 border-l border-zinc-100 dark:border-zinc-800">
              <div class="flex flex-col">
                <span class="text-[9px] font-black text-zinc-400 uppercase tracking-widest">Endpoint</span>
                <span class="text-xs font-mono font-bold text-zinc-700 dark:text-zinc-300 truncate max-w-[200px]">{{ globalAIConfig.default_ai_base_url }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Section: Personal AI Configs -->
        <section class="space-y-6">
          <div class="flex items-center space-x-2 px-1">
            <div class="w-1 h-4 bg-zinc-900 dark:bg-white rounded-full"></div>
            <h2 class="text-xs font-black uppercase tracking-widest text-zinc-900 dark:text-white">已连接的引擎 Nodes ({{ userOwnedConfigs.length }})</h2>
          </div>

          <div v-if="userOwnedConfigs.length === 0" class="py-20 border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-3xl flex flex-col items-center justify-center text-center">
            <el-icon :size="48" class="text-zinc-200 mb-4"><Cpu /></el-icon>
            <h3 class="text-zinc-900 dark:text-white font-bold tracking-tight">暂无可用推理节点</h3>
            <p class="text-zinc-400 text-xs mt-1 mb-6">点击右上角按钮添加您的第一个 API 引擎</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="config in userOwnedConfigs" 
              :key="config.id"
              class="group bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-subtle hover:border-zinc-400 dark:hover:border-zinc-600 transition-all duration-300"
            >
              <div class="flex justify-between items-start mb-6">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 rounded-xl bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center text-zinc-900 dark:text-white border border-zinc-100 dark:border-zinc-700 group-hover:scale-105 transition-transform">
                    <el-icon :size="18"><Cpu /></el-icon>
                  </div>
                  <div>
                    <h3 class="text-sm font-bold text-zinc-900 dark:text-white group-hover:text-brand-accent transition-colors">{{ config.name }}</h3>
                    <div class="flex items-center space-x-1.5 mt-0.5">
                      <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                      <span class="text-[9px] font-black text-zinc-400 uppercase tracking-widest">Active</span>
                    </div>
                  </div>
                </div>
                <div class="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click="handleEdit(config)" class="p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-400 transition-all"><el-icon><Edit /></el-icon></button>
                  <button @click="handleDelete(config.id)" class="p-1.5 rounded-lg hover:bg-rose-50 text-zinc-400 hover:text-rose-600 transition-all"><el-icon><Delete /></el-icon></button>
                </div>
              </div>

              <div class="space-y-4 mb-6">
                <div class="flex flex-col space-y-1">
                  <span class="text-[9px] font-black text-zinc-400 uppercase tracking-widest px-0.5">Deployment Endpoint</span>
                  <div class="p-2.5 rounded-xl bg-zinc-50 dark:bg-zinc-950/50 border border-zinc-100 dark:border-zinc-800/50 text-xs font-mono font-bold text-zinc-600 dark:text-zinc-400 truncate">
                    {{ config.baseUrl }}
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div class="flex flex-col space-y-1">
                    <span class="text-[9px] font-black text-zinc-400 uppercase tracking-widest px-0.5">Model ID</span>
                    <span class="text-xs font-bold text-zinc-900 dark:text-white truncate">{{ config.model }}</span>
                  </div>
                  <div class="flex flex-col space-y-1">
                    <span class="text-[9px] font-black text-zinc-400 uppercase tracking-widest px-0.5">Security Key</span>
                    <span class="text-xs font-mono font-bold text-zinc-900 dark:text-white">{{ maskApiKey(config.maskedApiKey || '') }}</span>
                  </div>
                </div>
              </div>

              <div class="pt-4 border-t border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
                <button 
                  @click="handleTestConnection(config.id)"
                  :loading="testingConfigId === config.id"
                  class="flex items-center space-x-2 text-[10px] font-black uppercase tracking-[0.1em] text-zinc-500 hover:text-zinc-900 dark:hover:text-white transition-colors"
                >
                  <el-icon v-if="testingConfigId !== config.id"><Connection /></el-icon>
                  <el-icon v-else class="animate-spin"><Loading /></el-icon>
                  <span>测试引擎连通性</span>
                </button>
                <div v-if="config.isDefault" class="px-2 py-0.5 rounded bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 text-[8px] font-black uppercase tracking-tighter">Default</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Section: Inference Parameters -->
        <section class="space-y-6">
          <div class="flex items-center space-x-2 px-1">
            <div class="w-1 h-4 bg-zinc-900 dark:bg-white rounded-full"></div>
            <h2 class="text-xs font-black uppercase tracking-widest text-zinc-900 dark:text-white">推理运行参数 Core Parameters</h2>
          </div>

          <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-8 shadow-subtle">
            <el-form label-position="top" class="studio-settings-form">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
                <div class="space-y-8">
                  <el-form-item label="TEMPERATURE (随机性控制)">
                    <div class="flex justify-between items-center mb-2">
                      <p class="text-[11px] text-zinc-500 font-medium leading-relaxed">较低的值使模型更确定，较高的值增加创意。</p>
                      <span class="text-xs font-mono font-bold text-zinc-900 dark:text-white bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded">{{ configStore.temperature }}</span>
                    </div>
                    <el-slider v-model="configStore.temperature" :min="0" :max="2" :step="0.1" class="studio-slider" />
                  </el-form-item>
                </div>
                <div class="space-y-8">
                  <el-form-item label="MAX TOKENS (单次回复上限)">
                    <div class="flex justify-between items-center mb-2">
                      <p class="text-[11px] text-zinc-500 font-medium leading-relaxed">限制生成文本的最大长度，防止消耗过高成本。</p>
                      <span class="text-xs font-mono font-bold text-zinc-900 dark:text-white bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded">{{ configStore.maxTokens }}</span>
                    </div>
                    <el-slider v-model="configStore.maxTokens" :min="100" :max="8000" :step="100" class="studio-slider" />
                  </el-form-item>
                </div>
              </div>
              
              <div class="mt-10 pt-8 border-t border-zinc-100 dark:border-zinc-800 flex justify-end">
                <el-button 
                  type="primary" 
                  @click="saveDefaultParams"
                  class="h-10 px-8 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-bold border-none shadow-premium"
                >
                  <el-icon class="mr-2"><Check /></el-icon>应用全局参数
                </el-button>
              </div>
            </el-form>
          </div>
        </section>
      </div>
    </main>

    <!-- Unified Engine Dialog -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingConfig ? '编辑推理节点' : '连接新节点'"
      width="600px"
      class="studio-dark-dialog"
    >
      <el-form :model="formData" label-position="top" class="p-2 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="节点名称 NAME">
            <el-input v-model="formData.name" placeholder="例如：OpenAI 生产节点" class="studio-input-minimal" />
          </el-form-item>
          <el-form-item label="模型 ID MODEL">
            <el-select v-model="formData.model" filterable allow-create class="studio-select-minimal w-full">
              <el-option v-for="m in configStore.availableModels" :key="m.id" :label="m.name" :value="m.id" />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item label="API BASE URL">
          <el-input v-model="formData.baseUrl" placeholder="https://api.openai.com/v1" class="studio-input-minimal" />
        </el-form-item>

        <el-form-item label="引擎密钥 AUTH KEY">
          <el-input v-model="formData.apiKey" type="password" :placeholder="editingConfig ? '留空则保持原密钥不变' : 'sk-...'" show-password class="studio-input-minimal" />
        </el-form-item>

        <el-form-item label="备注说明 DESCRIPTION (OPTIONAL)">
          <el-input v-model="formData.description" type="textarea" :rows="2" class="studio-textarea-minimal" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex items-center justify-between w-full px-2">
          <button @click="handleTestInDialog" :loading="testing" class="text-[10px] font-black uppercase tracking-widest text-zinc-400 hover:text-zinc-900 transition-colors">
            引擎自检 Test Connection
          </button>
          <div class="flex space-x-3">
            <el-button @click="showAddDialog = false" class="rounded-lg h-10 px-6 border-zinc-200">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving" class="rounded-lg h-10 px-10 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-bold border-none">
              {{ editingConfig ? '同步配置' : '建立连接' }}
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '@/store/config'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Cpu, Check, Connection, Setting, Loading } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import type { AIConfig } from '@/store/config'
import { aiConfigAPI, systemAPI } from '@/api'

const router = useRouter()
const configStore = useConfigStore()
const userStore = useUserStore()

const globalAIConfig = ref<any>(null)
const showAddDialog = ref(false)
const editingConfig = ref<AIConfig | null>(null)
const saving = ref(false)
const testing = ref(false)
const testingConfigId = ref<number | null>(null)

const userOwnedConfigs = computed(() => configStore.aiConfigs.filter(config => !config.isGlobal))
const formData = reactive({ name: '', baseUrl: 'https://api.openai.com/v1', apiKey: '', model: 'gpt-3.5-turbo', description: '' })

onMounted(async () => {
  await configStore.loadAIConfigs()
  if (userStore.userInfo?.role === 'admin') await loadGlobalAIConfig()
})

async function loadGlobalAIConfig() {
  try { const res = await systemAPI.getGlobalAIConfig(); globalAIConfig.value = res.data } catch {}
}

const navigateToGlobalConfig = () => router.push('/admin/global-ai-config')
const maskApiKey = (key: string) => key.length <= 8 ? '***' : key.substring(0, 4) + '...' + key.substring(key.length - 4)

function handleEdit(config: AIConfig) {
  editingConfig.value = config
  Object.assign(formData, { name: config.name, baseUrl: config.baseUrl, apiKey: config.apiKey, model: config.model, description: config.description || '' })
  showAddDialog.value = true
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这个节点连接吗？已保存的相关数据将失效。', '移除确认', { type: 'warning' })
    await configStore.deleteAIConfig(id)
    ElMessage.success('已断开连接')
  } catch {}
}

async function handleSave() {
  if (!formData.name || !formData.baseUrl || (!editingConfig.value && !formData.apiKey)) { ElMessage.warning('必填项不能为空'); return }
  saving.value = true
  try {
    if (editingConfig.value) {
      const updateData: any = { name: formData.name, baseUrl: formData.baseUrl, model: formData.model, description: formData.description }
      if (formData.apiKey) updateData.apiKey = formData.apiKey
      await configStore.updateAIConfig(editingConfig.value.id, updateData)
    } else await configStore.addAIConfig(formData)
    ElMessage.success('配置已就绪')
    showAddDialog.value = false; resetForm()
  } finally { saving.value = false }
}

const resetForm = () => { editingConfig.value = null; Object.assign(formData, { name: '', baseUrl: 'https://api.openai.com/v1', apiKey: '', model: 'gpt-3.5-turbo', description: '' }) }
const saveDefaultParams = () => { configStore.saveDefaultParams(); ElMessage.success('参数已应用到全局') }

async function handleTestConnection(id: number) {
  testingConfigId.value = id
  try { await aiConfigAPI.test(id); ElMessage.success('连接链路正常') } finally { testingConfigId.value = null }
}

async function handleTestInDialog() {
  if (!formData.apiKey) return
  testing.value = true
  try { 
    await aiConfigAPI.testConnection({ name: formData.name, base_url: formData.baseUrl, api_key: formData.apiKey, model: formData.model, description: formData.description })
    ElMessage.success('测试成功，节点可用')
  } finally { testing.value = false }
}
</script>

<style scoped>
.studio-settings-form :deep(.el-form-item__label) {
  @apply text-[10px] font-black uppercase tracking-[0.2em] text-zinc-900 dark:text-white mb-4;
}

.studio-input-minimal :deep(.el-input__wrapper), 
.studio-select-minimal :deep(.el-input__wrapper) {
  @apply bg-transparent !shadow-none border border-zinc-200 dark:border-zinc-800 rounded-lg h-10 px-3 transition-all hover:border-zinc-400 focus:border-zinc-900 dark:focus:border-zinc-100;
}

.studio-textarea-minimal :deep(.el-textarea__inner) {
  @apply bg-transparent !shadow-none border border-zinc-200 dark:border-zinc-800 rounded-lg p-3 transition-all hover:border-zinc-400 focus:border-zinc-900 dark:focus:border-zinc-100 text-sm leading-relaxed;
}

:deep(.studio-slider.el-slider) {
  --el-slider-main-bg-color: #0f172a;
  --el-slider-runway-bg-color: #f1f5f9;
  --el-slider-stop-bg-color: #0f172a;
}

.dark :deep(.studio-slider.el-slider) {
  --el-slider-main-bg-color: #ffffff;
  --el-slider-runway-bg-color: #1e293b;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
