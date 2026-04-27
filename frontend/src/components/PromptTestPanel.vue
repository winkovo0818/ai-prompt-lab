<template>
  <div class="h-full overflow-y-auto p-5 space-y-5 scrollbar-hide">
    <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 shadow-subtle space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-sm font-bold text-zinc-900 dark:text-white">测试集</h3>
          <p class="text-[11px] text-zinc-400 mt-1">保存后可自动跑 smoke，手动可跑完整回归</p>
        </div>
        <el-button size="small" type="primary" @click="createDefaultSuite" :loading="loading">
          新建
        </el-button>
      </div>

      <el-select v-model="selectedSuiteId" placeholder="选择测试集" class="w-full" @change="loadSelectedSuite">
        <el-option
          v-for="suite in suites"
          :key="suite.id"
          :label="`${suite.name} · ${suite.suite_type}`"
          :value="suite.id"
        />
      </el-select>
    </div>

    <div v-if="editingSuite" class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 shadow-subtle space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <el-input v-model="editingSuite.name" placeholder="测试集名称" />
        <el-select v-model="editingSuite.suite_type">
          <el-option label="Smoke" value="smoke" />
          <el-option label="Full" value="full" />
        </el-select>
      </div>

      <el-input v-model="editingSuite.description" type="textarea" :rows="2" placeholder="说明" />

      <div class="grid grid-cols-2 gap-3">
        <el-select v-model="editingSuite.baseline_mode">
          <el-option label="上一版本" value="previous_version" />
          <el-option label="固定版本" value="fixed_version" />
        </el-select>
        <el-input-number
          v-model="editingSuite.fixed_baseline_version"
          :disabled="editingSuite.baseline_mode !== 'fixed_version'"
          :min="1"
          class="w-full"
          placeholder="基线版本"
        />
      </div>

      <div class="flex items-center justify-between rounded-lg bg-zinc-50 dark:bg-zinc-950 border border-zinc-100 dark:border-zinc-800 px-3 py-2">
        <span class="text-xs font-bold text-zinc-600 dark:text-zinc-300">保存后自动跑</span>
        <el-switch v-model="editingSuite.auto_run_on_save" />
      </div>

      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-black text-zinc-400 uppercase tracking-widest">测试用例 JSON</span>
          <span class="text-[10px] text-zinc-400">{{ parsedCaseCount }} cases</span>
        </div>
        <el-input v-model="testCasesText" type="textarea" :rows="10" class="font-mono" />
      </div>

      <div class="grid grid-cols-2 gap-3">
        <el-button @click="saveSuite" :loading="saving" class="rounded-lg">保存测试集</el-button>
        <el-button type="primary" @click="runSuite" :loading="running" class="rounded-lg">运行测试</el-button>
      </div>
    </div>

    <div v-if="latestRun" class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 shadow-subtle space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-sm font-bold text-zinc-900 dark:text-white">最近运行</h3>
          <p class="text-[11px] text-zinc-400 mt-1">v{{ latestRun.candidate_version }} vs v{{ latestRun.baseline_version || '-' }}</p>
        </div>
        <el-tag :type="latestRun.summary?.passed_gate ? 'success' : 'danger'" size="small">
          {{ latestRun.summary?.passed_gate ? '通过' : '未通过' }}
        </el-tag>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="metric-card">
          <span>通过率</span>
          <strong>{{ latestRun.summary?.pass_rate || 0 }}%</strong>
        </div>
        <div class="metric-card">
          <span>退化</span>
          <strong>{{ latestRun.summary?.regression_cases || 0 }}</strong>
        </div>
        <div class="metric-card">
          <span>评分</span>
          <strong>{{ latestRun.summary?.avg_quality_score || 0 }}</strong>
        </div>
        <div class="metric-card">
          <span>耗时</span>
          <strong>{{ latestRun.summary?.avg_response_time || 0 }}s</strong>
        </div>
      </div>

      <div class="space-y-2">
        <div
          v-for="item in latestRun.results || []"
          :key="item.case_index"
          class="rounded-lg border border-zinc-100 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-950"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-zinc-800 dark:text-zinc-200">{{ item.name }}</span>
            <el-tag :type="item.passed ? 'success' : 'danger'" size="small">{{ item.passed ? 'PASS' : 'FAIL' }}</el-tag>
          </div>
          <p class="text-[11px] text-zinc-500 line-clamp-3 whitespace-pre-wrap">{{ item.candidate_output }}</p>
        </div>
      </div>
    </div>

    <div v-if="!loading && suites.length === 0" class="py-10 text-center text-xs text-zinc-400">
      还没有测试集，点击“新建”生成一个 smoke 模板。
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { testSuiteAPI } from '@/api'
import { useConfigStore } from '@/store/config'

interface Props {
  promptId: number
  version: number
}

interface TestSuite {
  id: number
  name: string
  description?: string
  suite_type: 'smoke' | 'full'
  is_active: boolean
  auto_run_on_save: boolean
  baseline_mode: 'previous_version' | 'fixed_version'
  fixed_baseline_version?: number | null
  test_cases: any[]
}

const props = defineProps<Props>()
const configStore = useConfigStore()
const loading = ref(false)
const saving = ref(false)
const running = ref(false)
const suites = ref<TestSuite[]>([])
const selectedSuiteId = ref<number | null>(null)
const editingSuite = ref<TestSuite | null>(null)
const latestRun = ref<any>(null)
const testCasesText = ref('[]')

const parsedCaseCount = computed(() => {
  try {
    const parsed = JSON.parse(testCasesText.value)
    return Array.isArray(parsed) ? parsed.length : 0
  } catch {
    return 0
  }
})

onMounted(async () => {
  await loadSuites()
})

async function loadSuites() {
  loading.value = true
  try {
    const response = await testSuiteAPI.getByPrompt(props.promptId) as any
    suites.value = response.data
    if (suites.value.length > 0) {
      selectedSuiteId.value = suites.value[0].id
      loadSelectedSuite()
      await loadLatestRun()
    }
  } finally {
    loading.value = false
  }
}

function loadSelectedSuite() {
  const suite = suites.value.find(item => item.id === selectedSuiteId.value)
  editingSuite.value = suite ? JSON.parse(JSON.stringify(suite)) : null
  testCasesText.value = JSON.stringify(editingSuite.value?.test_cases || [], null, 2)
}

async function createDefaultSuite() {
  loading.value = true
  try {
    const response = await testSuiteAPI.create({
      prompt_id: props.promptId,
      name: 'Smoke 回归测试',
      suite_type: 'smoke',
      auto_run_on_save: true,
      test_cases: [
        {
          name: '基础输出检查',
          variables: {},
          required_keywords: [],
          forbidden_keywords: ['无法回答', '抱歉'],
          min_quality_score: 6,
          max_response_time: 20
        }
      ]
    }) as any
    suites.value.unshift(response.data)
    selectedSuiteId.value = response.data.id
    loadSelectedSuite()
    ElMessage.success('测试集已创建')
  } finally {
    loading.value = false
  }
}

async function saveSuite() {
  if (!editingSuite.value) return

  let testCases: any[] = []
  try {
    const parsed = JSON.parse(testCasesText.value)
    if (!Array.isArray(parsed)) throw new Error('测试用例必须是数组')
    testCases = parsed
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '测试用例 JSON 无效')
    return
  }

  saving.value = true
  try {
    const response = await testSuiteAPI.update(editingSuite.value.id, {
      ...editingSuite.value,
      test_cases: testCases
    }) as any
    const index = suites.value.findIndex(item => item.id === response.data.id)
    if (index !== -1) suites.value[index] = response.data
    editingSuite.value = response.data
    ElMessage.success('测试集已保存')
  } finally {
    saving.value = false
  }
}

async function runSuite() {
  if (!editingSuite.value) return
  running.value = true
  try {
    await saveSuite()
    const response = await testSuiteAPI.run(editingSuite.value.id, {
      candidate_version: props.version,
      trigger_source: 'manual',
      model: configStore.selectedModel,
      temperature: 0,
      enable_evaluation: true
    }) as any
    latestRun.value = response.data
    ElMessage.success('测试运行完成')
  } finally {
    running.value = false
  }
}

async function loadLatestRun() {
  const response = await testSuiteAPI.getRuns({ prompt_id: props.promptId, limit: 1 }) as any
  latestRun.value = response.data.items?.[0] || null
}
</script>

<style scoped>
.metric-card {
  @apply flex flex-col rounded-lg border border-zinc-100 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 p-3;
}

.metric-card span {
  @apply text-[10px] font-bold text-zinc-400 uppercase tracking-widest;
}

.metric-card strong {
  @apply mt-1 text-sm font-black text-zinc-900 dark:text-zinc-100;
}
</style>
