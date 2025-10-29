<template>
  <div class="compare-test-page">
    <Header />
    
    <div class="content-container">
      <div class="test-config-panel">
        <div class="panel-header">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
          </svg>
          <h2>测试配置</h2>
        </div>

        <el-form :model="testConfig" label-position="top" class="config-form">
          <el-form-item label="测试名称">
            <el-input
              v-model="testConfig.test_name"
              placeholder="给这次测试起个名字"
            />
          </el-form-item>

          <el-form-item label="选择 Prompts（2-5个）">
            <el-select
              v-model="testConfig.prompt_ids"
              multiple
              filterable
              placeholder="选择要对比的 Prompts"
              class="w-full"
              @change="handlePromptSelect"
            >
              <el-option
                v-for="prompt in availablePrompts"
                :key="prompt.id"
                :label="prompt.title"
                :value="prompt.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="AI 配置">
            <el-select v-model="testConfig.aiConfigId" class="w-full" placeholder="选择 AI 配置">
              <el-option
                v-for="config in configStore.aiConfigs"
                :key="config.id"
                :label="config.name"
                :value="config.id"
              >
                <div style="display: flex; align-items: center; gap: 8px;">
                  <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                      <span style="font-weight: 500;">{{ config.name }}</span>
                      <el-tag v-if="config.isGlobal" size="small" type="success">全局</el-tag>
                    </div>
                    <div style="font-size: 12px; color: #909399;">{{ config.model }}</div>
                  </div>
                </div>
              </el-option>
            </el-select>
            <div v-if="configStore.aiConfigs.length === 0" style="margin-top: 8px; font-size: 12px; color: #f56c6c;">
              请先在设置页面添加 AI 配置
              <el-button link type="primary" @click="$router.push('/settings')">去设置</el-button>
            </div>
          </el-form-item>

          <el-form-item label="变量配置">
            <VariableInputWithFile
              :variables="allVariables"
              v-model="testConfig.input_variables"
              v-model:file-model-value="testConfig.file_variables"
            />
          </el-form-item>

          <el-form-item label="高级选项">
            <el-checkbox v-model="testConfig.enable_evaluation" class="mb-2">
              启用AI质量评测
            </el-checkbox>
            <div class="option-hint">自动评测输出质量（准确性、相关性、流畅度等）</div>
            <el-checkbox v-model="testConfig.generate_report">
              生成对比分析报告
            </el-checkbox>
            <div class="option-hint">AI生成详细的对比分析和优化建议</div>
          </el-form-item>

          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              @click="handleRunTest"
              :loading="running"
              :disabled="!canRunTest"
              class="run-test-button"
            >
              <el-icon><CaretRight /></el-icon>
              <span>{{ running ? '测试进行中...' : '运行 A/B 测试' }}</span>
            </el-button>
            
            <el-button
              size="large"
              @click="resetForm"
              :disabled="running"
            >
              <el-icon><RefreshLeft /></el-icon>
              重置配置
            </el-button>
          </div>
        </el-form>
      </div>

      <div class="test-results-panel">
        <div class="results-header">
          <div class="results-title">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
            </svg>
            <h2>测试结果</h2>
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <el-button @click="viewComparisonReport" v-if="testResults" type="primary">
              <el-icon><Document /></el-icon>
              <span>查看对比报告</span>
            </el-button>
            <el-button @click="showTestHistory" class="history-btn">
              <el-icon><Clock /></el-icon>
              <span>历史记录</span>
              <el-badge :value="testHistory.length" :max="99" v-if="testHistory.length > 0" />
            </el-button>
          </div>
        </div>

        <div v-if="running" class="loading-container">
          <div class="loading-content">
            <el-icon class="loading-icon" :size="60">
              <Loading />
            </el-icon>
            <h3 class="loading-title">正在运行 A/B 测试...</h3>
            <p class="loading-desc">正在调用 AI 生成内容，这可能需要 10-30 秒</p>
            <p class="loading-hint">测试包含 {{ testConfig.prompt_ids.length }} 个 Prompt 版本</p>
          </div>
        </div>

        <div v-else-if="testResults">
          <!-- 测试参数信息 -->
          <div class="test-params-box">
            <div class="params-header">
              <el-icon><Setting /></el-icon>
              <span>测试参数</span>
            </div>
            <div class="params-content">
              <div class="param-item">
                <span class="param-label">测试名称：</span>
                <span class="param-value">{{ testResults.test_name }}</span>
              </div>
              <div class="param-item">
                <span class="param-label">AI 模型：</span>
                <span class="param-value">{{ testResults.model || '默认模型' }}</span>
              </div>
              <div class="param-item">
                <span class="param-label">测试时间：</span>
                <span class="param-value">{{ formatDate(testResults.created_at) }}</span>
              </div>
              <div v-if="testResults.input_variables && Object.keys(testResults.input_variables).length > 0" class="param-item variables-item">
                <span class="param-label">输入变量：</span>
                <div class="variables-display">
                  <pre>{{ JSON.stringify(testResults.input_variables, null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>

          <!-- 测试结果卡片 -->
          <div class="results-grid">
          <div
            v-for="(result, index) in testResults.results"
            :key="index"
            class="result-card"
            :class="{ 'best-result': isBestResult(result) }"
          >
            <div class="card-header">
              <div class="card-title">
                <span class="rank-badge">{{ index + 1 }}</span>
                <h3>{{ result.prompt_title }}</h3>
              </div>
              <el-tag v-if="isBestResult(result)" type="success" effect="dark" size="large">
                <el-icon><Trophy /></el-icon>
                最佳
              </el-tag>
            </div>

            <div class="result-stats">
              <div class="stat-item stat-time">
                <div class="stat-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="stat-content">
                  <span class="label">响应时间</span>
                  <span class="value">{{ result.response_time }}s</span>
                </div>
              </div>
              <div class="stat-item stat-token">
                <div class="stat-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
                  </svg>
                </div>
                <div class="stat-content">
                  <span class="label">Token 用量</span>
                  <span class="value">{{ result.total_tokens }}</span>
                </div>
              </div>
              <div class="stat-item stat-cost">
                <div class="stat-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="stat-content">
                  <span class="label">调用成本</span>
                  <span class="value">{{ formatCost(result.cost) }}</span>
                </div>
              </div>
              
              <!-- 质量评分 -->
              <div v-if="result.quality_score" class="stat-item stat-quality">
                <div class="stat-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                  </svg>
                </div>
                <div class="stat-content">
                  <span class="label">质量评分</span>
                  <span class="value">{{ result.quality_score.toFixed(1) }}/10</span>
                </div>
              </div>
            </div>
            
            <!-- 质量评测详情 -->
            <div v-if="result.evaluation_details" class="evaluation-details">
              <el-button 
                text 
                @click="result._showDetails = !result._showDetails"
                class="details-toggle"
              >
                <el-icon><Document /></el-icon>
                {{ result._showDetails ? '收起' : '查看' }}评测详情
                <el-icon><component :is="result._showDetails ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
              </el-button>
              
              <div v-show="result._showDetails" class="details-content">
                <!-- 评分卡片 -->
                <div class="scores-grid">
                  <div class="score-card">
                    <div class="score-label">准确性</div>
                    <div class="score-value">{{ result.evaluation_details.accuracy_score.toFixed(1) }}</div>
                    <el-progress 
                      :percentage="result.evaluation_details.accuracy_score * 10" 
                      :stroke-width="6"
                      :show-text="false"
                    />
                  </div>
                  <div class="score-card">
                    <div class="score-label">相关性</div>
                    <div class="score-value">{{ result.evaluation_details.relevance_score.toFixed(1) }}</div>
                    <el-progress 
                      :percentage="result.evaluation_details.relevance_score * 10" 
                      :stroke-width="6"
                      :show-text="false"
                      color="#67c23a"
                    />
                  </div>
                  <div class="score-card">
                    <div class="score-label">流畅度</div>
                    <div class="score-value">{{ result.evaluation_details.fluency_score.toFixed(1) }}</div>
                    <el-progress 
                      :percentage="result.evaluation_details.fluency_score * 10" 
                      :stroke-width="6"
                      :show-text="false"
                      color="#e6a23c"
                    />
                  </div>
                  <div class="score-card">
                    <div class="score-label">创意性</div>
                    <div class="score-value">{{ result.evaluation_details.creativity_score.toFixed(1) }}</div>
                    <el-progress 
                      :percentage="result.evaluation_details.creativity_score * 10" 
                      :stroke-width="6"
                      :show-text="false"
                      color="#909399"
                    />
                  </div>
                  <div class="score-card">
                    <div class="score-label">安全性</div>
                    <div class="score-value">{{ result.evaluation_details.safety_score.toFixed(1) }}</div>
                    <el-progress 
                      :percentage="result.evaluation_details.safety_score * 10" 
                      :stroke-width="6"
                      :show-text="false"
                      color="#f56c6c"
                    />
                  </div>
                </div>
                
                <!-- 详细分析 -->
                <div class="analysis-sections">
                  <div v-if="result.evaluation_details.strengths && result.evaluation_details.strengths.length > 0" class="analysis-box strengths">
                    <div class="analysis-title">
                      <el-icon><CircleCheck /></el-icon>
                      优点
                    </div>
                    <ul>
                      <li v-for="(strength, idx) in result.evaluation_details.strengths" :key="idx">{{ strength }}</li>
                    </ul>
                  </div>
                  
                  <div v-if="result.evaluation_details.weaknesses && result.evaluation_details.weaknesses.length > 0" class="analysis-box weaknesses">
                    <div class="analysis-title">
                      <el-icon><WarningFilled /></el-icon>
                      缺点
                    </div>
                    <ul>
                      <li v-for="(weakness, idx) in result.evaluation_details.weaknesses" :key="idx">{{ weakness }}</li>
                    </ul>
                  </div>
                  
                  <div v-if="result.evaluation_details.suggestions && result.evaluation_details.suggestions.length > 0" class="analysis-box suggestions">
                    <div class="analysis-title">
                      <el-icon><Memo /></el-icon>
                      改进建议
                    </div>
                    <ul>
                      <li v-for="(suggestion, idx) in result.evaluation_details.suggestions" :key="idx">{{ suggestion }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div class="result-output">
              <div class="output-label">输出内容</div>
              <div class="output-text">{{ result.output }}</div>
            </div>
          </div>

          <el-empty
            v-if="testResults.results.length === 0"
            description="暂无测试结果"
          />
          </div>
        </div>

        <div v-else class="empty-state">
          <el-empty description="配置测试参数后点击运行">
            <el-icon :size="64" class="text-gray-300"><DataAnalysis /></el-icon>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 历史记录抽屉 -->
    <el-drawer
      v-model="historyDrawerVisible"
      title="测试历史"
      size="50%"
      direction="rtl"
    >
      <div class="history-list">
        <div
          v-for="history in testHistory"
          :key="history.id"
          class="history-item"
        >
          <div class="history-header">
            <div>
              <h3 class="history-title">{{ history.test_name }}</h3>
              <p class="history-meta">
                {{ new Date(history.created_at).toLocaleString('zh-CN') }}
                · {{ history.results?.length || 0 }} 个版本
              </p>
            </div>
            <div class="history-actions">
              <el-button size="small" @click="viewHistoryResult(history)">
                查看
              </el-button>
              <el-button
                size="small"
                type="danger"
                :icon="Delete"
                @click="deleteHistory(history.id)"
              />
            </div>
          </div>
          
          <div class="history-summary">
            <div
              v-for="(result, idx) in (history.results || []).slice(0, 3)"
              :key="idx"
              class="summary-item"
            >
              <span class="prompt-title">{{ result.prompt_title }}</span>
              <span class="response-time">{{ result.response_time }}s</span>
            </div>
          </div>
        </div>

        <el-empty
          v-if="testHistory.length === 0"
          description="暂无测试历史"
        />
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usePromptStore } from '@/store/prompt'
import { useConfigStore } from '@/store/config'
import { abtestAPI } from '@/api'
import { extractVariables } from '@/utils/markdown'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Clock, Delete, CaretRight, RefreshLeft, Trophy, Document, Setting } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import VariableInputWithFile from '@/components/VariableInputWithFile.vue'

const promptStore = usePromptStore()
const configStore = useConfigStore()

const running = ref(false)
const availablePrompts = ref<any[]>([])
const selectedPrompts = ref<any[]>([])
const testHistory = ref<any[]>([])
const historyDrawerVisible = ref(false)

const testConfig = reactive({
  test_name: '',
  prompt_ids: [] as number[],
  aiConfigId: '',
  input_variables: {} as Record<string, string>,
  file_variables: {} as Record<string, number>,
  enable_evaluation: true,
  generate_report: true
})

const testResults = ref<any>(null)

const canRunTest = computed(() => {
  return (
    testConfig.test_name &&
    testConfig.prompt_ids.length >= 2 &&
    testConfig.prompt_ids.length <= 5 &&
    testConfig.aiConfigId
  )
})

const allVariables = computed(() => {
  const vars = new Set<string>()
  selectedPrompts.value.forEach(prompt => {
    const promptVars = extractVariables(prompt.content)
    promptVars.forEach(v => vars.add(v))
  })
  return Array.from(vars)
})

onMounted(async () => {
  await loadPrompts()
  await configStore.loadAIConfigs()
  await loadTestHistory()
})

async function loadPrompts() {
  await promptStore.fetchPrompts({ limit: 100 })
  availablePrompts.value = promptStore.prompts
}

async function handlePromptSelect() {
  // 加载选中Prompt的完整详情（包含content）
  selectedPrompts.value = []
  
  for (const promptId of testConfig.prompt_ids) {
    try {
      const promptDetail = await promptStore.fetchPromptDetail(promptId)
      selectedPrompts.value.push(promptDetail)
    } catch (error) {
      console.error(`加载Prompt ${promptId} 详情失败:`, error)
    }
  }
  
  console.log('已加载的Prompts:', selectedPrompts.value)
  console.log('提取的变量:', allVariables.value)
}

async function handleRunTest() {
  if (!canRunTest.value) {
    ElMessage.warning('请正确配置测试参数')
    return
  }

  running.value = true
  testResults.value = null

  try {
    const aiConfig = configStore.aiConfigs.find(c => c.id === Number(testConfig.aiConfigId))
    if (!aiConfig) {
      ElMessage.error('请选择 AI 配置')
      running.value = false
      return
    }

    console.log('开始运行AB测试，配置:', {
      test_name: testConfig.test_name,
      prompt_ids: testConfig.prompt_ids,
      input_variables: testConfig.input_variables,
      file_variables: testConfig.file_variables
    })

    const response = await abtestAPI.create({
      test_name: testConfig.test_name,
      prompt_ids: testConfig.prompt_ids,
      input_variables: testConfig.input_variables,
      file_variables: testConfig.file_variables,
      model: aiConfig.model,
      api_base_url: aiConfig.baseUrl,
      api_key: aiConfig.apiKey,
      enable_evaluation: testConfig.enable_evaluation,
      generate_report: testConfig.generate_report
    })

    console.log('AB测试完整响应:', response)
    console.log('response.data:', response.data)
    
    testResults.value = response.data
    console.log('设置testResults.value为:', testResults.value)
    console.log('testResults.value.results:', testResults.value?.results)
    
    ElMessage.success('测试完成')
    
    // 刷新历史记录列表
    await loadTestHistory()
  } catch (error: any) {
    console.error('测试失败:', error)
    ElMessage.error(error.response?.data?.message || error.message || '测试失败')
  } finally {
    running.value = false
  }
}

function resetForm() {
  testConfig.test_name = ''
  testConfig.prompt_ids = []
  testConfig.input_variables = {}
  testConfig.file_variables = {}
  selectedPrompts.value = []
  testResults.value = null
  ElMessage.success('已重置配置')
}

async function loadTestHistory() {
  try {
    const response = await abtestAPI.getList({ skip: 0, limit: 50 }) as any
    console.log('历史记录响应:', response)
    console.log('response.data:', response.data)
    testHistory.value = response.data.items || []
    console.log('加载测试历史:', testHistory.value)
  } catch (error) {
    console.error('加载测试历史失败:', error)
  }
}

function showTestHistory() {
  historyDrawerVisible.value = true
}

function viewHistoryResult(history: any) {
  testResults.value = history
  historyDrawerVisible.value = false
  ElMessage.success('已加载历史测试结果')
}

async function deleteHistory(historyId: number) {
  try {
    await abtestAPI.delete(historyId)
    ElMessage.success('删除成功')
    await loadTestHistory()
    // 如果删除的是当前显示的结果，清空结果
    if (testResults.value?.id === historyId) {
      testResults.value = null
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

function isBestResult(result: any): boolean {
  if (!testResults.value?.results || testResults.value.results.length < 2) return false
  
  const results = testResults.value.results
  
  // 如果有质量评分，优先使用质量评分
  if (result.quality_score) {
    const scores = results.map((r: any) => r.quality_score || 0)
    const maxScore = Math.max(...scores)
    
    // 只有当分数明显高于其他时才标记为最佳（避免所有都相同）
    const countMax = scores.filter(s => s === maxScore).length
    if (countMax === results.length) {
      // 如果所有分数都相同，都不标记为最佳
      return false
    }
    
    return result.quality_score === maxScore
  }
  
  // 否则使用综合评分：响应时间越短、成本越低越好
  const minTime = Math.min(...results.map((r: any) => r.response_time))
  const minCost = Math.min(...results.map((r: any) => r.cost))
  
  // 计算综合得分（响应时间和成本归一化后相加）
  const scores = results.map((r: any) => {
    const timeScore = minTime / r.response_time
    const costScore = minCost / r.cost
    return timeScore + costScore
  })
  
  const maxScore = Math.max(...scores)
  const currentScore = (minTime / result.response_time) + (minCost / result.cost)
  
  // 只有明显最优的才标记
  const countMax = scores.filter(s => Math.abs(s - maxScore) < 0.01).length
  if (countMax === results.length) {
    return false
  }
  
  return Math.abs(currentScore - maxScore) < 0.01
}

async function viewComparisonReport() {
  if (!testResults.value?.id) {
    ElMessage.warning('无法加载报告')
    return
  }
  
  try {
    const response = await abtestAPI.getReport(testResults.value.id)
    
    const report = response.data
    
    // 显示报告内容
    ElMessageBox.alert(
      `
        <div style="text-align: left;">
          <h3 style="margin-top: 0;">对比分析报告</h3>
          
          <div style="background: #f0f9ff; padding: 12px; border-radius: 8px; margin: 12px 0;">
            <strong>📝 分析摘要：</strong>
            <p style="margin: 8px 0 0 0;">${report.summary || '暂无摘要'}</p>
          </div>
          
          ${report.winner_reason ? `
            <div style="background: #f0fdf4; padding: 12px; border-radius: 8px; margin: 12px 0;">
              <strong>🏆 获胜原因：</strong>
              <p style="margin: 8px 0 0 0;">${report.winner_reason}</p>
            </div>
          ` : ''}
          
          ${report.recommendations && report.recommendations.length > 0 ? `
            <div style="background: #fef3c7; padding: 12px; border-radius: 8px; margin: 12px 0;">
              <strong>💡 优化建议：</strong>
              <ul style="margin: 8px 0 0 0; padding-left: 20px;">
                ${report.recommendations.map(r => `<li>${r}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>
      `,
      '对比分析报告',
      {
        confirmButtonText: '关闭',
        dangerouslyUseHTMLString: true,
        customClass: 'report-dialog',
        customStyle: {
          width: '800px',
          maxWidth: '90vw'
        }
      }
    )
  } catch (error: any) {
    console.error('加载报告失败:', error)
    
    // 如果报告不存在，尝试生成
    if (error.response?.status === 404 || error.response?.data?.code === 4006) {
      try {
        await abtestAPI.regenerateReport(testResults.value.id)
        ElMessage.success('报告生成成功，请再次查看')
      } catch (genError) {
        ElMessage.error('生成报告失败')
      }
    } else {
      ElMessage.error('加载报告失败')
    }
  }
}

// 辅助函数
const formatCost = (cost: number): string => {
  return `$${cost.toFixed(6)}`
}

const truncateText = (text: string, maxLength: number): string => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.compare-test-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
}

.content-container {
  flex: 1;
  display: grid;
  grid-template-columns: 420px 1fr;
  overflow: hidden;
  gap: 0;
}

.test-config-panel {
  background: white;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 2px solid #f3f4f6;
  background: linear-gradient(to bottom, #fafafa, #ffffff);
}

.panel-header svg {
  width: 24px;
  height: 24px;
  color: #3b82f6;
  flex-shrink: 0;
}

.panel-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.config-form {
  padding: 1.5rem;
  flex: 1;
}

.action-buttons {
  margin-top: auto;
  padding: 1.5rem;
  background: white;
  border-top: 2px solid #f3f4f6;
  display: flex;
  gap: 1rem;
}

.run-test-button {
  flex: 1;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  background: #3b82f6;
  border: none;
  transition: all 0.2s ease;
}

.run-test-button:hover {
  background: #2563eb;
}

.run-test-button:disabled {
  background: #dcdfe6;
}

.action-buttons .el-button:not(.run-test-button) {
  height: 48px;
  font-size: 15px;
}

.test-results-panel {
  padding: 1.5rem;
  overflow-y: auto;
  background: #f9fafb;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem 1.25rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.results-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.results-title svg {
  width: 24px;
  height: 24px;
  color: #3b82f6;
  flex-shrink: 0;
}

.results-title h2 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.history-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.loading-content {
  text-align: center;
  padding: 2rem;
}

.loading-icon {
  color: #409eff;
  margin-bottom: 1.5rem;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #303133;
  margin: 0 0 0.75rem 0;
}

.loading-desc {
  font-size: 0.875rem;
  color: #606266;
  margin: 0 0 0.5rem 0;
}

.loading-hint {
  font-size: 0.875rem;
  color: #909399;
  margin: 0;
}

/* 测试参数框 */
.test-params-box {
  background: white;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.params-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #24292e;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e1e4e8;
}

.params-header .el-icon {
  font-size: 1.1rem;
  color: #0366d6;
}

.params-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.75rem;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.param-item.variables-item {
  grid-column: 1 / -1;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
}

.param-label {
  color: #586069;
  font-weight: 500;
  white-space: nowrap;
}

.param-value {
  color: #24292e;
  font-weight: 600;
}

.variables-display {
  width: 100%;
  background: #f6f8fa;
  border: 1px solid #d1d5da;
  border-radius: 6px;
  padding: 0;
  overflow: hidden;
}

.variables-display pre {
  margin: 0;
  padding: 1rem;
  font-family: 'Consolas', 'Monaco', 'SF Mono', 'Courier New', monospace;
  font-size: 0.875rem;
  color: #24292e;
  line-height: 1.6;
  overflow-x: auto;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 1.25rem;
}

.result-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s;
}

.result-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.result-card.best-result {
  border-color: #10b981;
  background: linear-gradient(to bottom, #ffffff, #f0fdf4);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f3f4f6;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.rank-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 700;
  flex-shrink: 0;
}

.card-title h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-stats {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #fafafa;
}

.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 20px;
  height: 20px;
}

.stat-time .stat-icon {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #d97706;
}

.stat-token .stat-icon {
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  color: #16a34a;
}

.stat-cost .stat-icon {
  background: linear-gradient(135deg, #fce7f3, #fbcfe8);
  color: #db2777;
}

.stat-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item .label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-item .value {
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
}

.result-output {
  margin-top: 1rem;
}

.output-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.output-text {
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  font-family: 'Consolas', 'Monaco', monospace;
  line-height: 1.6;
  max-height: 200px;
  overflow-y: auto;
  color: #374151;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.loading-container {
  padding: 2rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 0.5rem;
}

.history-item {
  background: linear-gradient(to bottom, #ffffff, #fafbfc);
  border: 1px solid #e1e4e8;
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.history-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #409eff, #66b1ff);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.history-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.12);
  transform: translateY(-2px);
}

.history-item:hover::before {
  opacity: 1;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.history-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #24292e;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.01em;
}

.history-meta {
  font-size: 0.875rem;
  color: #6a737d;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.history-actions {
  display: flex;
  gap: 0.5rem;
}

.history-summary {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  padding-top: 1rem;
  border-top: 1px solid #e1e4e8;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #f6f8fa 0%, #ffffff 100%);
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.summary-item:hover {
  background: linear-gradient(135deg, #ffffff 0%, #f6f8fa 100%);
  border-color: #c8e1ff;
  transform: translateX(4px);
}

.summary-item .prompt-title {
  color: #24292e;
  flex: 1;
  font-weight: 500;
}

.summary-item .response-time {
  color: #0366d6;
  font-weight: 600;
  font-size: 0.8125rem;
  padding: 0.25rem 0.625rem;
  background: #e8f4fd;
  border-radius: 12px;
}

.option-hint {
  font-size: 0.75rem;
  color: #909399;
  margin-top: 4px;
  margin-bottom: 8px;
}

.stat-quality .stat-icon {
  background: linear-gradient(135deg, #fef3c7, #fde047);
  color: #eab308;
}

.evaluation-details {
  margin-top: 1rem;
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.details-toggle {
  width: 100%;
  justify-content: center;
  font-size: 14px;
  color: #606266;
  padding: 8px 0;
}

.details-toggle:hover {
  color: #409eff;
}

.details-content {
  margin-top: 1rem;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.score-card {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
}

.score-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.analysis-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-box {
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid;
}

.analysis-box.strengths {
  background: #f0f9ff;
  border-left-color: #67c23a;
}

.analysis-box.weaknesses {
  background: #fef3f2;
  border-left-color: #f56c6c;
}

.analysis-box.suggestions {
  background: #fffbeb;
  border-left-color: #e6a23c;
}

.analysis-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.analysis-box ul {
  margin: 0;
  padding-left: 20px;
}

.analysis-box li {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 4px;
}

.mb-2 {
  margin-bottom: 0.5rem;
}
</style>

