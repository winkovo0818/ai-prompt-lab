<template>
  <div class="prompt-editor-page min-h-screen bg-white dark:bg-zinc-950 flex flex-col overflow-hidden">
    <Header />
    
    <!-- Workspace Area -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Main Content (Editor) -->
      <div class="flex-1 flex flex-col min-w-0 bg-white dark:bg-zinc-900 shadow-sm border-r border-zinc-200 dark:border-zinc-800">
        
        <!-- Editor Toolbar (IDE Style) -->
        <div class="h-12 border-b border-zinc-100 dark:border-zinc-800 px-4 flex items-center justify-between shrink-0 bg-white/50 dark:bg-zinc-900/50 backdrop-blur-sm">
          <div class="flex items-center space-x-4">
            <button @click="goBack" class="p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-500 transition-all">
              <el-icon :size="16"><ArrowLeft /></el-icon>
            </button>
            <div class="h-4 w-px bg-zinc-200 dark:bg-zinc-800"></div>
            <div class="flex flex-col leading-tight">
              <span class="text-[13px] font-bold text-zinc-900 dark:text-zinc-100 line-clamp-1 tracking-tight">
                {{ formData.title || '未命名项目' }}
              </span>
            </div>
            <div v-if="teamShared" class="flex items-center space-x-1.5 px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700">
              <el-icon :size="11" class="text-zinc-400"><UserFilled /></el-icon>
              <span class="text-[9px] font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-tighter">{{ teamInfo?.team_name }}</span>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <div class="flex items-center space-x-1 mr-2 pr-2 border-r border-zinc-100 dark:border-zinc-800">
              <el-tooltip content="Git 仓库" placement="bottom">
                <button v-if="isEditMode" @click="goToRepo" class="studio-tool-btn"><el-icon :size="14"><Connection /></el-icon></button>
              </el-tooltip>
              <el-tooltip content="历史版本" placement="bottom">
                <button v-if="isEditMode" @click="handleCompareWithPrevious" :disabled="!canCompare" class="studio-tool-btn"><el-icon :size="14"><Clock /></el-icon></button>
              </el-tooltip>
            </div>

            <el-button 
              type="primary" 
              size="small" 
              @click="handleSave" 
              :loading="saving"
              :disabled="!canEdit"
              class="rounded-md font-bold px-4 h-7.5 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-none hover:opacity-90 shadow-sm"
            >
              保存修改
            </el-button>
            
            <button 
              @click="handleRun" 
              :disabled="running"
              class="flex items-center space-x-1.5 px-3 h-7.5 rounded-md bg-brand-accent text-white font-bold text-xs hover:opacity-90 transition-all shadow-sm"
            >
              <el-icon v-if="!running"><CaretRight /></el-icon>
              <el-icon v-else class="animate-spin"><Loading /></el-icon>
              <span>立即运行</span>
            </button>
          </div>
        </div>

        <!-- Editor Workspace -->
        <div class="flex-1 overflow-y-auto p-6 md:p-10 scrollbar-hide bg-white dark:bg-zinc-900">
          <div class="max-w-4xl mx-auto space-y-12">
            <!-- Header Section -->
            <section class="space-y-4">
              <el-input
                v-model="formData.title"
                placeholder="实验项目标题..."
                class="studio-input-huge"
                :disabled="!canEdit"
              />
              <el-input
                v-model="formData.description"
                type="textarea"
                :rows="1"
                autosize
                placeholder="添加描述信息，定义实验目标..."
                class="studio-textarea-subtle"
                :disabled="!canEdit"
              />
            </section>

            <!-- Editor Section -->
            <section class="space-y-3">
              <div class="flex items-center justify-between ml-0.5">
                <div class="flex items-center space-x-2">
                  <label class="text-[10px] font-black text-zinc-400 uppercase tracking-widest">核心提示词 (Instructions)</label>
                </div>
                <span class="text-[9px] text-zinc-400 font-mono tracking-tighter font-bold">{{ formData.content.length }} 字符</span>
              </div>
              <div class="relative group border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-hidden shadow-subtle focus-within:border-brand-accent transition-all">
                <PromptCodeEditor
                  v-model="formData.content"
                  placeholder="在此输入您的提示词指令。使用 {{变量名}} 来定义动态输入..."
                  :disabled="!canEdit"
                  @input="handleContentChange"
                  class="border-none"
                />
              </div>
              <PromptStructureGuide :content="formData.content" class="mt-4" />
            </section>

            <!-- Bottom Section -->
            <section class="flex flex-wrap items-center gap-4 pt-8 border-t border-zinc-100 dark:border-zinc-800">
              <div class="flex flex-col space-y-1.5 flex-1 min-w-[200px]">
                <el-select
                  v-model="formData.tags"
                  multiple
                  filterable
                  allow-create
                  placeholder="为项目添加标签分类..."
                  class="carbon-select-clean"
                  :disabled="!canEdit"
                >
                  <el-option v-for="tag in commonTags" :key="tag" :label="tag" :value="tag" />
                </el-select>
              </div>
              <div class="flex items-center space-x-2">
                <el-switch v-model="formData.is_public" size="small" :disabled="!canEdit" />
                <span class="text-[11px] font-bold text-zinc-500 uppercase tracking-tight">公开分享</span>
              </div>
              <div v-if="isEditMode && isOwner" class="ml-auto">
                <el-button type="danger" text @click="handleDelete" class="hover:bg-rose-50 rounded-lg text-xs font-bold">
                  <el-icon class="mr-1"><Delete /></el-icon>删除
                </el-button>
              </div>
            </section>
          </div>
        </div>
      </div>

      <!-- Right Panel (Inspector) -->
      <div class="w-[420px] flex flex-col bg-zinc-50 dark:bg-zinc-950 shrink-0">
        <el-tabs v-model="activeTab" class="studio-inspector-tabs flex-1 flex flex-col overflow-hidden">
          
          <el-tab-pane label="变量" name="variables">
            <template #label>
              <div class="flex items-center space-x-1.5">
                <el-icon :size="13"><Ticket /></el-icon>
                <span>变量</span>
              </div>
            </template>
            <div class="p-5 overflow-y-auto h-full scrollbar-hide">
              <VariableInputWithFile
                :variables="variables"
                :content="formData.content"
                v-model="variableValues"
                v-model:file-model-value="fileVariableValues"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="结果" name="result">
            <template #label>
              <div class="flex items-center space-x-1.5">
                <el-icon :size="13"><CaretRight /></el-icon>
                <span>结果</span>
              </div>
            </template>
            <div class="h-full overflow-hidden">
              <ResultViewer
                :result="executionResult"
                :loading="running"
                :auto-show-rendered="autoShowRendered"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="分析" name="analysis">
            <template #label>
              <div class="flex items-center space-x-1.5">
                <el-icon :size="13"><MagicStick /></el-icon>
                <span>分析</span>
              </div>
            </template>
            <div class="p-5 h-full overflow-y-auto scrollbar-hide">
              <div class="flex flex-col space-y-4">
                <el-button type="primary" @click="handleAnalyze" :loading="analyzing" class="w-full rounded-lg shadow-sm">
                  AI 深度质量分析
                </el-button>
                <div v-if="analysisResult" class="space-y-4">
                  <!-- Analysis result rendering... -->
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="参数" name="settings">
            <template #label>
              <el-icon :size="13"><Setting /></el-icon>
            </template>
            <div class="p-5 space-y-6">
              <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-5 shadow-subtle">
                <el-form label-position="top">
                  <el-form-item label="执行模型 (LLM Model)">
                    <el-select v-model="configStore.selectedModel" class="w-full carbon-select-clean">
                      <el-option
                        v-for="model in configStore.availableModels"
                        :key="model.id"
                        :label="model.name"
                        :value="model.id"
                      />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="Temperature">
                    <el-slider v-model="configStore.temperature" :min="0" :max="2" :step="0.1" />
                  </el-form-item>
                </el-form>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePromptStore } from '@/store/prompt'
import { useConfigStore } from '@/store/config'
import { useUserStore } from '@/store/user'
import { runAPI, promptAPI, promptAnalysisAPI } from '@/api'
import { ArrowLeft, Connection, Clock, CaretRight, Ticket, MagicStick, Setting, Delete, UserFilled, Loading } from '@element-plus/icons-vue'
import { extractVariables } from '@/utils/markdown'
import { ElMessage, ElMessageBox } from 'element-plus'
import Header from '@/components/Layout/Header.vue'
import VariableInputWithFile from '@/components/VariableInputWithFile.vue'
import ResultViewer from '@/components/ResultViewer.vue'
import PromptCodeEditor from '@/components/PromptCodeEditor.vue'
import PromptStructureGuide from '@/components/PromptStructureGuide.vue'

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
const analyzing = ref(false)
const analysisResult = ref<any>(null)
const canEdit = ref(true)
const teamShared = ref(false)
const teamInfo = ref<any>(null)
const autoShowRendered = ref(false)
const promptOwnerId = ref<number | null>(null)
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
    canEdit.value = prompt.can_edit !== false
    teamShared.value = prompt.team_shared || false
    teamInfo.value = prompt.team_info || null
  } catch (error) { router.push('/prompts') }
}

async function handleSave() {
  if (!formData.title || !formData.content) { ElMessage.warning('请填写标题和内容'); return }
  saving.value = true
  try {
    if (isEditMode.value) await promptStore.updatePrompt(Number(route.params.id), formData)
    else {
      const newPrompt = await promptStore.createPrompt(formData)
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

async function handleAnalyze() {
  if (!formData.content) return
  analyzing.value = true
  try {
    const res = await promptAnalysisAPI.analyze({ content: formData.content, title: formData.title })
    analysisResult.value = res.data.analysis
    activeTab.value = 'analysis'
  } catch (e) { ElMessage.error('分析失败') } finally { analyzing.value = false }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除此实验项目吗？', '删除确认', { type: 'warning' })
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
.studio-tool-btn {
  @apply p-1.5 rounded-md text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 dark:hover:text-white dark:hover:bg-zinc-800 transition-colors;
}

.studio-input-huge :deep(.el-input__wrapper) {
  @apply text-2xl font-bold px-0 bg-transparent !shadow-none !border-none;
}

.studio-textarea-subtle :deep(.el-textarea__inner) {
  @apply bg-transparent !shadow-none px-0 text-zinc-500 dark:text-zinc-400 border-none resize-none text-[13px] font-medium leading-relaxed;
}

.carbon-select-clean :deep(.el-input__wrapper) {
  @apply rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 !shadow-none py-1.5;
}

:deep(.studio-inspector-tabs) {
  @apply h-full flex flex-col;
}

:deep(.studio-inspector-tabs .el-tabs__header) {
  @apply m-0 px-4 bg-white dark:bg-zinc-900 border-b border-zinc-100 dark:border-zinc-800 shrink-0;
}

:deep(.studio-inspector-tabs .el-tabs__content) {
  @apply flex-1 p-0 overflow-hidden;
}

:deep(.studio-inspector-tabs .el-tabs__item) {
  @apply text-[11px] font-bold uppercase tracking-wider h-12 py-0 transition-all;
}

:deep(.studio-inspector-tabs .el-tabs__active-bar) {
  @apply bg-zinc-900 dark:bg-white h-[2px];
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
