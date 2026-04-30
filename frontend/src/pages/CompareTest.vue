<template>
  <div class="compare-test-page min-h-screen bg-white dark:bg-zinc-950 flex flex-col overflow-hidden">
    <Header />
    
    <div class="flex-1 flex overflow-hidden">
      <!-- Sidebar Configuration: Crisp IDE Style -->
      <aside class="w-[380px] bg-zinc-50 dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 flex flex-col shrink-0 overflow-y-auto scrollbar-hide">
        <div class="p-6 h-16 border-b border-zinc-100 dark:border-zinc-800/50 flex items-center justify-between sticky top-0 bg-zinc-50/80 dark:bg-zinc-900/80 backdrop-blur-md z-10">
          <div class="flex items-center space-x-2 text-zinc-900 dark:text-white">
            <el-icon :size="18"><Connection /></el-icon>
            <h2 class="text-xs font-black tracking-widest uppercase">对比测试实验室 Experiment</h2>
          </div>
          <button @click="resetForm" class="text-[9px] font-black uppercase tracking-widest text-zinc-400 hover:text-brand-accent transition-colors">
            Reset
          </button>
        </div>

        <div class="p-8 space-y-10">
          <!-- Setup Group -->
          <div class="space-y-6">
            <div class="space-y-4">
              <div class="flex flex-col space-y-1.5">
                <label class="text-[9px] font-black text-zinc-400 uppercase tracking-[0.2em] ml-0.5">实验名称 IDENTIFIER</label>
                <el-input v-model="testConfig.test_name" placeholder="例如：翻译性能对比 V2" class="studio-input-minimal" />
              </div>

              <div class="flex flex-col space-y-1.5">
                <label class="text-[9px] font-black text-zinc-400 uppercase tracking-[0.2em] ml-0.5">测试对象 CANDIDATES (2-5)</label>
                <el-select
                  v-model="testConfig.prompt_ids"
                  multiple
                  filterable
                  collapse-tags
                  collapse-tags-tooltip
                  placeholder="搜索并选择待测试提示词"
                  class="studio-select-minimal w-full"
                  @change="handlePromptSelect"
                >
                  <el-option v-for="p in availablePrompts" :key="p.id" :label="p.title" :value="p.id" />
                </el-select>
              </div>

              <div class="flex flex-col space-y-1.5">
                <label class="text-[9px] font-black text-zinc-400 uppercase tracking-[0.2em] ml-0.5">推理引擎 DEPLOYMENT</label>
                <el-select v-model="testConfig.aiConfigId" class="studio-select-minimal w-full">
                  <el-option v-for="config in configStore.aiConfigs" :key="config.id" :label="config.name" :value="config.id" />
                </el-select>
              </div>
            </div>

            <!-- Input Group -->
            <div class="space-y-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
              <label class="text-[9px] font-black text-zinc-400 uppercase tracking-[0.2em] ml-0.5">输入变量 Context Variables</label>
              <VariableInputWithFile
                :variables="allVariables"
                v-model="testConfig.input_variables"
                v-model:file-model-value="testConfig.file_variables"
              />
            </div>

            <!-- Features Group -->
            <div class="space-y-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
              <label class="text-[9px] font-black text-zinc-400 uppercase tracking-[0.2em] ml-0.5">智能评估 AI EVAL</label>
              <div class="flex items-center justify-between p-3 rounded-xl bg-white dark:bg-zinc-950 border border-zinc-100 dark:border-zinc-800">
                <span class="text-xs font-bold text-zinc-600 dark:text-zinc-400">启用 AI 质量自动打分</span>
                <el-switch v-model="testConfig.enable_evaluation" size="small" />
              </div>
            </div>
          </div>
        </div>

        <!-- Action Area -->
        <div class="mt-auto p-6 bg-white dark:bg-zinc-900 sticky bottom-0 border-t border-zinc-100 dark:border-zinc-800 shadow-premium">
          <el-button 
            type="primary" 
            size="large" 
            class="w-full h-12 rounded-xl font-black bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-none shadow-premium uppercase tracking-widest text-[11px]"
            :loading="running"
            :disabled="!canRunTest"
            @click="handleRunTest"
          >
            <el-icon class="mr-2" v-if="!running"><CaretRight /></el-icon>
            {{ running ? '分析中 Analyzing...' : '开启并行实验室 Run Test' }}
          </el-button>
        </div>
      </aside>

      <!-- Main Panel: Visualization Area -->
      <main class="flex-1 overflow-y-auto bg-white dark:bg-zinc-950 p-12 scrollbar-hide">
        <div class="max-w-6xl mx-auto">
          
          <div class="flex items-center justify-between mb-12">
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 rounded-2xl bg-zinc-900 dark:bg-white flex items-center justify-center text-white dark:text-zinc-900 shadow-premium">
                <el-icon :size="24"><Histogram /></el-icon>
              </div>
              <div>
                <h1 class="text-2xl font-black text-zinc-900 dark:text-white tracking-tight uppercase">平行对比分析 Analysis</h1>
                <p class="text-zinc-400 text-sm font-medium mt-0.5">多版本输出质量与性能指标横向对标</p>
              </div>
            </div>
          </div>

          <!-- Interaction States -->
          <div v-if="running" class="py-40 flex flex-col items-center justify-center">
            <div class="w-16 h-16 rounded-2xl bg-zinc-900 dark:bg-white flex items-center justify-center animate-pulse mb-8 shadow-premium">
              <img src="/favicon.svg" alt="" class="w-8 h-8 invert dark:invert-0" />
            </div>
            <h3 class="text-xl font-black text-zinc-900 dark:text-white mb-2 tracking-tight uppercase">并行分析中 Running...</h3>
            <p class="text-zinc-400 text-sm font-medium">正在调度 AI 引擎执行并计算质量分值，请稍后</p>
          </div>

          <div v-else-if="!testResults" class="py-40 flex flex-col items-center justify-center opacity-30">
            <el-icon :size="64" class="text-zinc-200"><DataAnalysis /></el-icon>
            <p class="mt-8 text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400">请配置左侧面板开启平行实验</p>
          </div>

          <!-- Results Grid -->
          <div v-else class="space-y-10 animate-fade-in">
            <!-- Winner Highlight -->
            <div v-if="bestResult" class="bg-zinc-900 dark:bg-white border border-transparent rounded-[2rem] p-8 flex items-center justify-between shadow-premium relative overflow-hidden group">
              <div class="absolute inset-0 bg-brand-accent/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
              <div class="flex items-center space-x-6 relative z-10">
                <div class="w-14 h-14 rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-soft">
                  <el-icon :size="28"><Trophy /></el-icon>
                </div>
                <div>
                  <h3 class="text-lg font-black text-white dark:text-zinc-900 tracking-tight uppercase">最佳表现 Best Performer</h3>
                  <p class="text-zinc-400 dark:text-zinc-500 text-sm mt-0.5">版本: {{ bestResult.prompt_title }} · 综合权衡响应与质量的最佳选型</p>
                </div>
              </div>
              <div class="text-4xl font-black text-emerald-500 relative z-10 tabular-nums">{{ bestResult.quality_score?.toFixed(1) || 'N/A' }}</div>
            </div>

            <!-- Detail Cards -->
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
              <div 
                v-for="(result, index) in testResults.results" 
                :key="index"
                class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-[1.5rem] p-8 transition-all duration-500 hover:border-zinc-400 dark:hover:border-zinc-600 shadow-subtle group"
                :class="{ 'ring-2 ring-emerald-500/40 border-emerald-500/40 bg-zinc-50/30 dark:bg-emerald-950/5': result === bestResult }"
              >
                <div class="flex justify-between items-start mb-8">
                  <div class="space-y-1">
                    <span class="text-[9px] font-black text-zinc-400 uppercase tracking-widest">Candidate #0{{ index + 1 }}</span>
                    <h4 class="text-lg font-bold text-zinc-900 dark:text-white tracking-tight group-hover:text-brand-accent transition-colors">{{ result.prompt_title }}</h4>
                  </div>
                  <div v-if="result.quality_score" class="flex flex-col items-end">
                    <span class="text-[9px] font-black text-zinc-400 uppercase tracking-tighter mb-1">SCORE</span>
                    <span class="text-2xl font-black text-zinc-900 dark:text-white tabular-nums">{{ result.quality_score.toFixed(1) }}</span>
                  </div>
                </div>

                <div class="grid grid-cols-3 gap-6 mb-8">
                  <div class="p-4 bg-zinc-50 dark:bg-zinc-950/50 rounded-2xl border border-zinc-100 dark:border-zinc-800">
                    <span class="text-[8px] font-black text-zinc-400 uppercase tracking-widest block mb-2">Latency</span>
                    <span class="text-sm font-bold text-zinc-800 dark:text-zinc-200 font-mono">{{ result.response_time }}s</span>
                  </div>
                  <div class="p-4 bg-zinc-50 dark:bg-zinc-950/50 rounded-2xl border border-zinc-100 dark:border-zinc-800">
                    <span class="text-[8px] font-black text-zinc-400 uppercase tracking-widest block mb-2">Tokens</span>
                    <span class="text-sm font-bold text-zinc-800 dark:text-zinc-200 font-mono">{{ result.total_tokens }}</span>
                  </div>
                  <div class="p-4 bg-zinc-50 dark:bg-zinc-950/50 rounded-2xl border border-zinc-100 dark:border-zinc-800">
                    <span class="text-[8px] font-black text-zinc-400 uppercase tracking-widest block mb-2">Cost (Est)</span>
                    <span class="text-sm font-bold text-zinc-800 dark:text-zinc-200 font-mono">${{ result.cost.toFixed(4) }}</span>
                  </div>
                </div>

                <div class="space-y-3">
                  <span class="text-[9px] font-black text-zinc-400 uppercase tracking-widest px-1">输出预览 Output Preview</span>
                  <div class="bg-white dark:bg-zinc-950 border border-zinc-100 dark:border-zinc-800/50 rounded-2xl p-6 max-h-[260px] overflow-y-auto scrollbar-hide shadow-inner">
                    <pre class="text-[13px] font-mono text-zinc-600 dark:text-zinc-400 whitespace-pre-wrap leading-relaxed">{{ result.output }}</pre>
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
import { Connection, CaretRight, Histogram, DataAnalysis, Trophy } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import VariableInputWithFile from '@/components/VariableInputWithFile.vue'

const promptStore = usePromptStore(); const configStore = useConfigStore()
const running = ref(false); const availablePrompts = ref<any[]>([]); const selectedPrompts = ref<any[]>([])
const testResults = ref<any>(null)
const testConfig = reactive({ test_name: '', prompt_ids: [] as number[], aiConfigId: '', input_variables: {}, file_variables: {}, enable_evaluation: true })

const canRunTest = computed(() => testConfig.test_name && testConfig.prompt_ids.length >= 2 && testConfig.aiConfigId)
const allVariables = computed(() => { const vars = new Set<string>(); selectedPrompts.value.forEach(p => extractVariables(p.content).forEach(v => vars.add(v))); return Array.from(vars) })
const bestResult = computed(() => {
  if (!testResults.value?.results) return null
  return [...testResults.value.results].sort((a: any, b: any) => (b.quality_score || 0) - (a.quality_score || 0))[0]
})

onMounted(async () => {
  await promptStore.fetchPrompts({ limit: 100 }); availablePrompts.value = promptStore.prompts
  await configStore.loadAIConfigs()
})

async function handlePromptSelect() {
  selectedPrompts.value = []
  for (const id of testConfig.prompt_ids) {
    try { selectedPrompts.value.push(await promptStore.fetchPromptDetail(id)) } catch {}
  }
}

async function handleRunTest() {
  running.value = true; testResults.value = null
  try {
    const ai = configStore.aiConfigs.find(c => c.id === Number(testConfig.aiConfigId))
    const res = await abtestAPI.create({
      test_name: testConfig.test_name,
      prompt_ids: testConfig.prompt_ids,
      input_variables: testConfig.input_variables,
      file_variables: testConfig.file_variables,
      enable_evaluation: testConfig.enable_evaluation,
      model: ai?.model,
      ai_config_id: ai?.id
    })
    testResults.value = res.data; ElMessage.success('测试运行成功')
  } catch { ElMessage.error('测试启动失败') } finally { running.value = false }
}

const resetForm = () => { Object.assign(testConfig, { test_name: '', prompt_ids: [], input_variables: {}, file_variables: {} }); selectedPrompts.value = []; testResults.value = null }
</script>

<style scoped>
.studio-input-minimal :deep(.el-input__wrapper), 
.studio-select-minimal :deep(.el-input__wrapper) {
  @apply bg-white dark:bg-zinc-950 !shadow-none border border-zinc-200 dark:border-zinc-800 rounded-xl h-11 px-3 transition-all hover:border-zinc-400 focus:border-zinc-900;
}

.animate-fade-in { animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
