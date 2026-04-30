<template>
  <div class="prompt-editor-page min-h-screen bg-zinc-50 dark:bg-zinc-950 flex flex-col overflow-hidden">
    <Header />
    
    <!-- Main Studio Workspace -->
    <div class="flex-1 flex overflow-hidden p-4 lg:p-6 gap-6">
      
      <!-- Editor Card: Immersive Writing Experience -->
      <main class="flex-1 bg-white dark:bg-zinc-900 rounded-3xl shadow-premium border border-zinc-200/50 dark:border-zinc-800/50 flex flex-col overflow-hidden transition-all duration-500">
        
        <!-- Editor Header/Toolbar -->
        <div class="h-16 px-8 flex items-center justify-between shrink-0 border-b border-zinc-100 dark:border-zinc-800/50">
          <div class="flex items-center space-x-4">
            <button @click="goBack" class="w-9 h-9 rounded-full bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-all">
              <el-icon :size="16"><ArrowLeft /></el-icon>
            </button>
            <div class="flex flex-col">
              <span class="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-400 leading-none mb-1">Editor Space</span>
              <span class="text-sm font-bold text-zinc-800 dark:text-zinc-200 tracking-tight">{{ isEditMode ? '编辑项目' : '新建实验' }}</span>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <div class="hidden md:flex items-center space-x-1 mr-3 pr-3 border-r border-zinc-100 dark:border-zinc-800">
              <el-tooltip content="Git 版本控制" placement="bottom">
                <button v-if="isEditMode" @click="goToRepo" class="w-8 h-8 rounded-lg text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-all">
                  <el-icon :size="16"><Connection /></el-icon>
                </button>
              </el-tooltip>
              <el-tooltip content="历史快照" placement="bottom">
                <button v-if="isEditMode" @click="handleCompareWithPrevious" :disabled="!canCompare" class="w-8 h-8 rounded-lg text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-all">
                  <el-icon :size="16"><Clock /></el-icon>
                </button>
              </el-tooltip>
            </div>

            <el-button 
              @click="handleSave" 
              :loading="saving"
              :disabled="!canEdit"
              class="h-9 px-5 rounded-xl font-bold text-xs uppercase tracking-wider border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-50"
            >
              保存 Save
            </el-button>
            
            <button 
              @click="handleRun" 
              :disabled="running"
              class="flex items-center space-x-2 px-6 h-9 rounded-xl bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-bold text-xs uppercase tracking-widest hover:opacity-90 active:scale-95 transition-all shadow-premium"
            >
              <el-icon v-if="!running" class="text-brand-accent"><CaretRight /></el-icon>
              <el-icon v-else class="animate-spin"><Loading /></el-icon>
              <span>立即运行 Run</span>
            </button>
          </div>
        </div>

        <!-- Content Area: Immersive Input -->
        <div class="flex-1 overflow-y-auto scrollbar-hide">
          <div class="max-w-4xl mx-auto py-12 px-8 space-y-12">
            
            <!-- Title & Description Section: Notion Style -->
            <section class="space-y-6">
              <div class="relative group">
                <input
                  v-model="formData.title"
                  placeholder="项目标题 Untitled..."
                  class="w-full bg-transparent text-4xl font-black text-zinc-900 dark:text-white placeholder:text-zinc-200 dark:placeholder:text-zinc-800 border-none outline-none tracking-tighter"
                  :disabled="!canEdit"
                />
              </div>
              <div class="relative">
                <textarea
                  v-model="formData.description"
                  placeholder="添加一些描述信息，明确这个 Prompt 的实验目标..."
                  class="w-full bg-transparent text-lg font-medium text-zinc-500 dark:text-zinc-400 placeholder:text-zinc-200 dark:placeholder:text-zinc-800 border-none outline-none resize-none leading-relaxed"
                  rows="1"
                  v-autosize
                  :disabled="!canEdit"
                ></textarea>
              </div>
            </section>

            <!-- Editor Core Section -->
            <section class="space-y-4">
              <div class="flex items-center justify-between px-1">
                <div class="flex items-center space-x-2">
                  <div class="w-1.5 h-1.5 rounded-full bg-brand-accent"></div>
                  <span class="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">Prompt Instructions</span>
                </div>
                <span class="text-[9px] font-mono font-bold text-zinc-300 dark:text-zinc-700 uppercase tracking-widest">{{ formData.content.length }} Chars</span>
              </div>
              
              <div class="rounded-3xl border border-zinc-100 dark:border-zinc-800 overflow-hidden shadow-inner-soft bg-zinc-50/30 dark:bg-zinc-950/20 focus-within:ring-4 focus-within:ring-brand-accent/5 transition-all">
                <PromptCodeEditor
                  v-model="formData.content"
                  placeholder="在此输入您的核心指令。使用 {{变量名}} 定义动态参数..."
                  :disabled="!canEdit"
                  class="min-h-[400px]"
                />
              </div>

              <!-- Inline Guide -->
              <div class="pt-4">
                <PromptStructureGuide :content="formData.content" />
              </div>
            </section>
          </div>
        </div>
      </main>

      <!-- Inspector Panel: Right Sidebar -->
      <aside class="w-[420px] bg-white dark:bg-zinc-900 rounded-3xl shadow-premium border border-zinc-200/50 dark:border-zinc-800/50 flex flex-col overflow-hidden shrink-0">
        <div class="flex-1 flex flex-col overflow-hidden">
          <el-tabs v-model="activeTab" class="studio-pill-tabs flex-1 flex flex-col">
            
            <el-tab-pane name="variables">
              <template #label>
                <div class="flex items-center space-x-2 px-2">
                  <el-icon :size="14"><Ticket /></el-icon>
                  <span>输入</span>
                </div>
              </template>
              <div class="p-6 h-full overflow-y-auto scrollbar-hide">
                <div class="mb-6">
                  <h3 class="text-xs font-black uppercase tracking-[0.2em] text-zinc-900 dark:text-white mb-1">变量配置 Variables</h3>
                  <p class="text-[11px] text-zinc-400 font-medium">配置实验输入并进行实时预览</p>
                </div>
                <VariableInputWithFile
                  :variables="variables"
                  :content="formData.content"
                  v-model="variableValues"
                  v-model:file-model-value="fileVariableValues"
                />
              </div>
            </el-tab-pane>

            <el-tab-pane name="result">
              <template #label>
                <div class="flex items-center space-x-2 px-2">
                  <el-icon :size="14"><CaretRight /></el-icon>
                  <span>执行</span>
                </div>
              </template>
              <div class="h-full overflow-hidden flex flex-col">
                <ResultViewer
                  :result="executionResult"
                  :loading="running"
                  :auto-show-rendered="autoShowRendered"
                />
              </div>
            </el-tab-pane>

            <el-tab-pane name="settings">
              <template #label>
                <el-icon :size="14"><Setting /></el-icon>
              </template>
              <div class="p-6 space-y-8 overflow-y-auto scrollbar-hide h-full">
                <div class="space-y-6">
                  <h3 class="text-xs font-black uppercase tracking-[0.2em] text-zinc-900 dark:text-white">运行参数 Config</h3>
                  
                  <el-form label-position="top" class="studio-settings-form">
                    <el-form-item label="推理引擎 LLM MODEL">
                      <el-select v-model="configStore.selectedModel" class="w-full carbon-select-premium" size="large">
                        <el-option
                          v-for="model in configStore.availableModels"
                          :key="model.id"
                          :label="model.name"
                          :value="model.id"
                        />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="随机性 TEMPERATURE">
                      <el-slider v-model="configStore.temperature" :min="0" :max="2" :step="0.1" class="px-2" />
                    </el-form-item>
                  </el-form>
                </div>

                <div class="pt-8 border-t border-zinc-100 dark:border-zinc-800 space-y-6">
                  <h3 class="text-xs font-black uppercase tracking-[0.2em] text-zinc-900 dark:text-white">分类管理 Meta</h3>
                  <el-select
                    v-model="formData.tags"
                    multiple
                    filterable
                    allow-create
                    placeholder="添加标签分组..."
                    class="carbon-select-premium w-full"
                    size="large"
                    :disabled="!canEdit"
                  >
                    <el-option v-for="tag in commonTags" :key="tag" :label="tag" :value="tag" />
                  </el-select>

                  <div class="flex items-center justify-between p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-2xl border border-zinc-100 dark:border-zinc-700/50">
                    <div class="flex flex-col">
                      <span class="text-xs font-bold text-zinc-700 dark:text-zinc-200">公开项目 Share</span>
                      <span class="text-[10px] text-zinc-400 font-medium">在市场中展示此 Prompt</span>
                    </div>
                    <el-switch v-model="formData.is_public" size="small" :disabled="!canEdit" />
                  </div>
                </div>

                <div v-if="isEditMode && isOwner" class="pt-12">
                  <el-button type="danger" text @click="handleDelete" class="w-full h-11 rounded-2xl bg-rose-50 dark:bg-rose-900/10 text-rose-500 font-bold text-xs uppercase tracking-widest hover:bg-rose-100 transition-all">
                    <el-icon class="mr-2"><Delete /></el-icon>永久删除项目
                  </el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, Directive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePromptStore } from '@/store/prompt'
import { useConfigStore } from '@/store/config'
import { useUserStore } from '@/store/user'
import { runAPI } from '@/api'
import { ArrowLeft, Connection, Clock, CaretRight, Ticket, Setting, Delete, Loading } from '@element-plus/icons-vue'
import { extractVariables } from '@/utils/markdown'
import { ElMessage, ElMessageBox } from 'element-plus'
import Header from '@/components/Layout/Header.vue'
import VariableInputWithFile from '@/components/VariableInputWithFile.vue'
import ResultViewer from '@/components/ResultViewer.vue'
import PromptCodeEditor from '@/components/PromptCodeEditor.vue'
import PromptStructureGuide from '@/components/PromptStructureGuide.vue'
// Custom directive for auto-resizing textarea
const vAutosize: Directive = {
  updated: (el) => {
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'
  },
  mounted: (el) => {
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'
  }
}

const route = useRoute()
const router = useRouter()
const promptStore = usePromptStore()
const configStore = useConfigStore()
const userStore = useUserStore()

const activeTab = ref('variables')
const saving = ref(false)
const running = ref(false)
const formData = reactive({ title: '', content: '', description: '', tags: [] as string[], is_public: false })
const variableValues = ref<Record<string, string>>({})
const fileVariableValues = ref<Record<string, number>>({})
const executionResult = ref<any>(null)
const versions = ref<any[]>([])
const canEdit = ref(true)
const teamShared = ref(false)
const teamInfo = ref<any>(null)
const autoShowRendered = ref(false)
const promptOwnerId = ref<number | null>(null)
const currentVersion = ref(1)
const isOwner = computed(() => promptOwnerId.value === userStore.userInfo?.id)
const isEditMode = computed(() => !!route.params.id)
const variables = computed(() => extractVariables(formData.content))
const commonTags = ['对话', '翻译', '写作', '代码', '分析', '创意', '教育', '商业']
const canCompare = computed(() => versions.value.length >= 2)

async function loadPrompt() {
  const id = Number(route.params.id)
  try {
    const prompt = await promptStore.fetchPromptDetail(id) as any
    formData.title = prompt.title
    formData.content = prompt.content || ''
    formData.description = prompt.description || ''
    formData.tags = prompt.tags || []
    formData.is_public = prompt.is_public
    promptOwnerId.value = prompt.user_id || null
    currentVersion.value = prompt.version || 1
    canEdit.value = prompt.can_edit !== false
    teamShared.value = prompt.team_shared || false
    teamInfo.value = prompt.team_info || null
  } catch (error) { router.push('/prompts') }
}

async function handleSave() {
  if (!formData.title || !formData.content) { ElMessage.warning('请填写标题和内容'); return }
  saving.value = true
  try {
    if (isEditMode.value) {
      const updatedPrompt = await promptStore.updatePrompt(Number(route.params.id), formData)
      currentVersion.value = updatedPrompt.version || currentVersion.value
    }
    else {
      const newPrompt = await promptStore.createPrompt(formData)
      currentVersion.value = newPrompt.version || 1
      router.replace(`/editor/${newPrompt.id}`)
    }
  } finally { saving.value = false }
}

async function handleRun() {
  if (!formData.content) { ElMessage.warning('请输入内容'); return }
  running.value = true
  executionResult.value = null
  activeTab.value = 'result'
  try {
    const response = await runAPI.execute({
      prompt_id: isEditMode.value ? Number(route.params.id) : undefined,
      prompt_content: formData.content,
      variables: variableValues.value,
      file_variables: fileVariableValues.value,
      model: configStore.selectedModel,
      temperature: configStore.temperature,
      max_tokens: configStore.maxTokens
    })
    executionResult.value = response.data
  } catch (error) { ElMessage.error('执行失败') } finally { running.value = false }
}

const goBack = () => router.push('/prompts')
const goToRepo = () => router.push(`/repo/${route.params.id}`)
const handleCompareWithPrevious = () => router.push(`/repo/${route.params.id}?compare=true`)

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除此实验项目吗？', '删除确认', { type: 'warning', customClass: 'studio-message-box danger' })
    await promptStore.deletePrompt(Number(route.params.id))
    goBack()
  } catch {}
}

const handleContentChange = () => {}

onMounted(async () => {
  await configStore.loadAvailableModels()
  if (isEditMode.value) await loadPrompt()
})
</script>

<style scoped>
.shadow-premium {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
}

.shadow-inner-soft {
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.03);
}

/* Studio Pill Tabs */
:deep(.studio-pill-tabs) {
  @apply h-full flex flex-col;
}

:deep(.studio-pill-tabs .el-tabs__header) {
  @apply m-0 p-4 bg-zinc-50/50 dark:bg-zinc-800/30 border-b border-zinc-100 dark:border-zinc-800 shrink-0;
}

:deep(.studio-pill-tabs .el-tabs__nav-wrap::after) {
  @apply hidden;
}

:deep(.studio-pill-tabs .el-tabs__nav) {
  @apply bg-zinc-200/50 dark:bg-zinc-800 p-1 rounded-2xl flex w-full;
}

:deep(.studio-pill-tabs .el-tabs__item) {
  @apply flex-1 text-center h-9 leading-9 rounded-xl text-[11px] font-black uppercase tracking-widest text-zinc-400 transition-all border-none !px-0;
}

:deep(.studio-pill-tabs .el-tabs__item.is-active) {
  @apply bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm;
}

:deep(.studio-pill-tabs .el-tabs__active-bar) {
  @apply hidden;
}

:deep(.studio-pill-tabs .el-tabs__content) {
  @apply flex-1 overflow-hidden p-0;
}

/* Settings Form */
:deep(.studio-settings-form .el-form-item__label) {
  @apply text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 mb-3 ml-0.5;
}

.carbon-select-premium :deep(.el-input__wrapper) {
  @apply rounded-2xl bg-zinc-50 dark:bg-zinc-800 border-none shadow-inner-soft h-11 px-4 transition-all;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>