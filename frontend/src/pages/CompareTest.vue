<template>
  <div class="compare-test-page min-h-screen bg-white dark:bg-zinc-950 flex flex-col overflow-hidden">
    <Header />
    
    <div class="flex-1 flex overflow-hidden">
      <!-- Sidebar Configuration -->
      <aside class="w-[380px] bg-zinc-50 dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 flex flex-col shrink-0 overflow-y-auto scrollbar-hide">
        <div class="p-6 border-b border-zinc-100 dark:border-zinc-800/50 flex items-center justify-between">
          <div class="flex items-center space-x-2 text-zinc-900 dark:text-white">
            <el-icon :size="18"><Connection /></el-icon>
            <h2 class="text-sm font-bold tracking-tight uppercase">A/B 对比实验配置</h2>
          </div>
          <button @click="resetForm" class="text-[10px] font-bold uppercase tracking-widest text-zinc-400 hover:text-brand-accent transition-colors">
            重置
          </button>
        </div>

        <div class="p-6 space-y-8">
          <div class="space-y-5">
            <div class="flex flex-col space-y-1.5">
              <label class="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.1em] ml-0.5">实验名称</label>
              <el-input v-model="testConfig.test_name" placeholder="例如：翻译效果对比 V2" class="studio-input-clean" />
            </div>

            <div class="flex flex-col space-y-1.5">
              <label class="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.1em] ml-0.5">选择实验项 (2-5个)</label>
              <el-select
                v-model="testConfig.prompt_ids"
                multiple
                filterable
                collapse-tags
                collapse-tags-tooltip
                placeholder="搜索并选择待测试项"
                class="studio-select-clean w-full"
                @change="handlePromptSelect"
              >
                <el-option v-for="p in availablePrompts" :key="p.id" :label="p.title" :value="p.id" />
              </el-select>
            </div>

            <div class="flex flex-col space-y-1.5">
              <label class="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.1em] ml-0.5">运行模型</label>
              <el-select v-model="testConfig.aiConfigId" class="studio-select-clean w-full">
                <el-option v-for="config in configStore.aiConfigs" :key="config.id" :label="config.name" :value="config.id" />
              </el-select>
            </div>
          </div>

          <div class="space-y-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
            <label class="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.1em] ml-0.5">变量与输入</label>
            <VariableInputWithFile
              :variables="allVariables"
              v-model="testConfig.input_variables"
              v-model:file-model-value="testConfig.file_variables"
            />
          </div>

          <div class="space-y-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
            <label class="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.1em] ml-0.5">智能评估</label>
            <div class="space-y-2 px-1">
              <el-checkbox v-model="testConfig.enable_evaluation" size="small"><span class="text-xs font-medium">启用 AI 质量自动评分</span></el-checkbox>
            </div>
          </div>
        </div>

        <div class="mt-auto p-6 bg-white dark:bg-zinc-900 sticky bottom-0 border-t border-zinc-100 dark:border-zinc-800 shadow-premium">
          <el-button 
            type="primary" 
            size="large" 
            class="w-full h-11 rounded-lg font-bold bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-none shadow-sm"
            :loading="running"
            :disabled="!canRunTest"
            @click="handleRunTest"
          >
            <el-icon class="mr-2"><CaretRight /></el-icon>
            {{ running ? '运行中...' : '开始对比测试' }}
          </el-button>
        </div>
      </aside>

      <!-- Results Display -->
      <main class="flex-1 overflow-y-auto bg-white dark:bg-zinc-950 p-8 md:p-12 scrollbar-hide">
        <div class="max-w-6xl mx-auto">
          <!-- Header Area -->
          <div class="flex items-center justify-between mb-10">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-xl bg-zinc-100 dark:bg-zinc-900 flex items-center justify-center text-zinc-900 dark:text-white border border-zinc-200 dark:border-zinc-800 shadow-subtle">
                <el-icon :size="20"><Histogram /></el-icon>
              </div>
              <h1 class="text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">测试结果分析</h1>
            </div>
          </div>

          <!-- Running Loader -->
          <div v-if="running" class="py-32 flex flex-col items-center justify-center">
            <div class="w-12 h-12 rounded-xl bg-zinc-900 dark:bg-white flex items-center justify-center animate-pulse mb-6">
              <img src="/favicon.svg" alt="" class="w-6 h-6 invert dark:invert-0" />
            </div>
            <h3 class="text-lg font-bold text-zinc-900 dark:text-white mb-2 tracking-tight">正在并行分析版本表现...</h3>
            <p class="text-zinc-400 text-sm">正在计算各项质量指标与性能数据，请稍候</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="!testResults" class="py-32 flex flex-col items-center justify-center opacity-40">
            <el-icon :size="48" class="text-zinc-300"><DataAnalysis /></el-icon>
            <p class="mt-6 text-xs font-bold uppercase tracking-widest text-zinc-400">配置左侧参数后开始实验</p>
          </div>

          <!-- Test Results Grid -->
          <div v-else class="space-y-8 compare-fade-in">
            <!-- Winner Summary -->
            <div v-if="bestResult" class="bg-zinc-900 dark:bg-white border border-transparent rounded-2xl p-6 flex items-center justify-between shadow-premium">
              <div class="flex items-center space-x-4">
                <div class="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center text-white">
                  <el-icon :size="20"><Trophy /></el-icon>
                </div>
                <div>
                  <h3 class="text-md font-bold text-white dark:text-zinc-900 tracking-tight">推荐版本：{{ bestResult.prompt_title }}</h3>
                  <p class="text-zinc-400 dark:text-zinc-500 text-xs">基于响应速度、Token 成本与评估分数的综合推荐</p>
                </div>
              </div>
              <div class="text-2xl font-black text-emerald-500">{{ bestResult.quality_score?.toFixed(1) || 'BEST' }}</div>
            </div>

            <!-- Result Cards Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div 
                v-for="(result, index) in testResults.results" 
                :key="index"
                class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden p-6 transition-all hover:border-zinc-400 dark:hover:border-zinc-600 shadow-subtle"
                :class="{ 'ring-2 ring-emerald-500/50 border-emerald-500/50': result === bestResult }"
              >
                <!-- Card Header -->
                <div class="flex justify-between items-start mb-6">
                  <div class="space-y-1">
                    <div class="flex items-center space-x-2">
                      <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">#{{ index + 1 }}</span>
                      <h4 class="font-bold text-zinc-900 dark:text-white tracking-tight">{{ result.prompt_title }}</h4>
                    </div>
                  </div>
                  <div v-if="result.quality_score" class="flex flex-col items-end leading-none">
                    <span class="text-[9px] font-bold text-zinc-400 uppercase tracking-tighter mb-1">SCORE</span>
                    <span class="text-xl font-bold text-zinc-900 dark:text-white">{{ result.quality_score.toFixed(1) }}</span>
                  </div>
                </div>

                <!-- Stats Bar -->
                <div class="grid grid-cols-3 gap-4 mb-6">
                  <div class="p-3 bg-zinc-50 dark:bg-zinc-950/50 rounded-lg flex flex-col leading-tight border border-zinc-100 dark:border-zinc-800">
                    <span class="text-[8px] font-bold text-zinc-400 uppercase mb-1">延迟</span>
                    <span class="text-[13px] font-bold text-zinc-800 dark:text-zinc-200 font-mono">{{ result.response_time }}s</span>
                  </div>
                  <div class="p-3 bg-zinc-50 dark:bg-zinc-950/50 rounded-lg flex flex-col leading-tight border border-zinc-100 dark:border-zinc-800">
                    <span class="text-[8px] font-bold text-zinc-400 uppercase mb-1">TOKENS</span>
                    <span class="text-[13px] font-bold text-zinc-800 dark:text-zinc-200 font-mono">{{ result.total_tokens }}</span>
                  </div>
                  <div class="p-3 bg-zinc-50 dark:bg-zinc-950/50 rounded-lg flex flex-col leading-tight border border-zinc-100 dark:border-zinc-800">
                    <span class="text-[8px] font-bold text-zinc-400 uppercase mb-1">预估成本</span>
                    <span class="text-[13px] font-bold text-zinc-800 dark:text-zinc-200 font-mono">${{ result.cost.toFixed(4) }}</span>
                  </div>
                </div>

                <!-- Output Area -->
                <div class="space-y-2">
                  <span class="text-[9px] font-bold text-zinc-400 uppercase tracking-widest ml-0.5">输出预览</span>
                  <div class="bg-zinc-50 dark:bg-zinc-950/50 rounded-xl p-4 border border-zinc-100 dark:border-zinc-800/50 max-h-[180px] overflow-y-auto scrollbar-hide">
                    <pre class="text-[12px] font-mono text-zinc-600 dark:text-zinc-400 whitespace-pre-wrap leading-relaxed">{{ result.output }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usePromptStore } from '@/store/prompt'
import { useConfigStore } from '@/store/config'
import { abtestAPI } from '@/api'
import { extractVariables } from '@/utils/markdown'
import { ElMessage } from 'element-plus'
import { Connection, CaretRight, Histogram, DataAnalysis, Clock, Trophy } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import VariableInputWithFile from '@/components/VariableInputWithFile.vue'

const promptStore = usePromptStore()
const configStore = useConfigStore()
const running = ref(false)
const availablePrompts = ref<any[]>([])
const selectedPrompts = ref<any[]>([])
const testResults = ref<any>(null)
const testConfig = reactive({ test_name: '', prompt_ids: [] as number[], aiConfigId: '', input_variables: {}, file_variables: {}, enable_evaluation: true })
const canRunTest = computed(() => testConfig.test_name && testConfig.prompt_ids.length >= 2 && testConfig.aiConfigId)
const allVariables = computed(() => { const vars = new Set<string>(); selectedPrompts.value.forEach(p => extractVariables(p.content).forEach(v => vars.add(v))); return Array.from(vars) })

const bestResult = computed(() => {
  if (!testResults.value?.results) return null
  const results = testResults.value.results
  return [...results].sort((a: any, b: any) => (b.quality_score || 0) - (a.quality_score || 0))[0]
})

onMounted(async () => {
  await promptStore.fetchPrompts({ limit: 100 })
  availablePrompts.value = promptStore.prompts
  await configStore.loadAIConfigs()
})

async function handlePromptSelect() {
  selectedPrompts.value = []
  for (const id of testConfig.prompt_ids) {
    try { selectedPrompts.value.push(await promptStore.fetchPromptDetail(id)) } catch (e) {}
  }
}

async function handleRunTest() {
  running.value = true
  testResults.value = null
  try {
    const ai = configStore.aiConfigs.find(c => c.id === Number(testConfig.aiConfigId))
    const res = await abtestAPI.create({ ...testConfig, model: ai?.model, api_base_url: ai?.baseUrl, api_key: ai?.apiKey })
    testResults.value = res.data
    ElMessage.success('实验运行完成')
  } catch (e) { ElMessage.error('实验运行失败') } finally { running.value = false }
}

const resetForm = () => { Object.assign(testConfig, { test_name: '', prompt_ids: [], input_variables: {}, file_variables: {} }); selectedPrompts.value = []; testResults.value = null }
</script>

<style scoped>
:deep(.studio-input-clean .el-input__wrapper), 
:deep(.studio-select-clean .el-input__wrapper) {
  @apply rounded-lg bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 !shadow-none py-1.5 transition-all;
}

.compare-fade-in { animation: compareFadeIn 0.5s ease-out forwards; }
@keyframes compareFadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
