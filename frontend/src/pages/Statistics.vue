<template>
  <div class="statistics-page min-h-screen bg-zinc-50 dark:bg-zinc-950 flex flex-col overflow-hidden">
    <Header />
    
    <main class="flex-1 overflow-y-auto scrollbar-hide py-12 px-6">
      <div class="max-w-[1400px] mx-auto space-y-12">
        
        <!-- Page Header -->
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8 px-1">
          <div class="space-y-1">
            <h1 class="text-2xl font-black text-zinc-900 dark:text-white tracking-tight uppercase">使用洞察 Insights</h1>
            <p class="text-zinc-500 text-sm font-medium">全维度分析 API 调用、Token 消耗及成本分布</p>
          </div>
          <div class="flex items-center space-x-3">
            <el-select v-model="selectedDays" @change="loadAllData" class="studio-select-minimal w-40">
              <el-option :value="7" label="最近 7 天" />
              <el-option :value="14" label="最近 14 天" />
              <el-option :value="30" label="最近 30 天" />
              <el-option :value="90" label="最近 90 天" />
            </el-select>
            <button @click="loadAllData" :class="{ 'animate-spin': loading }" class="p-2 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 text-zinc-500 hover:text-zinc-900 dark:hover:text-white transition-all">
              <el-icon><Refresh /></el-icon>
            </button>
          </div>
        </div>

        <!-- Overview Cards: Redesigned for High Signal -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-6" v-loading="loading">
          <div v-for="card in overviewCards" :key="card.label" class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-subtle flex flex-col justify-between">
            <div class="flex items-center justify-between mb-4">
              <span class="text-[10px] font-black text-zinc-400 uppercase tracking-[0.2em]">{{ card.label }}</span>
              <div class="w-8 h-8 rounded-lg bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center text-zinc-400">
                <el-icon :size="16"><component :is="card.icon" /></el-icon>
              </div>
            </div>
            <div class="space-y-1">
              <h2 class="text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">{{ card.value }}</h2>
              <p class="text-[10px] text-zinc-400 font-medium">{{ card.desc }}</p>
            </div>
          </div>
        </div>

        <!-- Charts Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Main Trend Chart -->
          <div class="lg:col-span-2 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-8 shadow-subtle">
            <div class="flex items-center justify-between mb-8">
              <div class="flex items-center space-x-2">
                <div class="w-1 h-4 bg-zinc-900 dark:bg-white rounded-full"></div>
                <h3 class="text-xs font-black uppercase tracking-widest text-zinc-900 dark:text-white">调用趋势 Time Series</h3>
              </div>
              <div class="flex bg-zinc-100 dark:bg-zinc-800 rounded-lg p-0.5">
                <button 
                  v-for="t in [{v:'calls',l:'次数'}, {v:'tokens',l:'TOKENS'}, {v:'cost',l:'成本'}]" 
                  :key="t.v"
                  @click="dailyChartType = t.v as any"
                  class="px-3 py-1 text-[9px] font-black uppercase rounded transition-all"
                  :class="dailyChartType === t.v ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm' : 'text-zinc-400 hover:text-zinc-600'"
                >
                  {{ t.l }}
                </button>
              </div>
            </div>
            <div class="h-[340px]" ref="dailyChartRef"></div>
          </div>

          <!-- Distribution Chart -->
          <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-8 shadow-subtle">
            <div class="flex items-center space-x-2 mb-8">
              <div class="w-1 h-4 bg-zinc-900 dark:bg-white rounded-full"></div>
              <h3 class="text-xs font-black uppercase tracking-widest text-zinc-900 dark:text-white">模型分布 Models</h3>
            </div>
            <div class="h-[340px]" ref="modelChartRef"></div>
          </div>

          <!-- Hourly Distribution -->
          <div class="lg:col-span-3 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-8 shadow-subtle">
            <div class="flex items-center space-x-2 mb-8">
              <div class="w-1 h-4 bg-zinc-900 dark:bg-white rounded-full"></div>
              <h3 class="text-xs font-black uppercase tracking-widest text-zinc-900 dark:text-white">24小时活动周期 Hourly Activity</h3>
            </div>
            <div class="h-[240px]" ref="hourlyChartRef"></div>
          </div>
        </div>

        <!-- Leaderboard Table -->
        <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden shadow-subtle">
          <div class="p-8 border-b border-zinc-100 dark:border-zinc-800">
            <div class="flex items-center space-x-2">
              <div class="w-1 h-4 bg-zinc-900 dark:bg-white rounded-full"></div>
              <h3 class="text-xs font-black uppercase tracking-widest text-zinc-900 dark:text-white">热点提示词排行 Top Prompts</h3>
            </div>
          </div>
          <el-table :data="topPrompts" v-loading="loading" class="studio-table">
            <el-table-column prop="title" label="提示词标题 PROMPT TITLE" min-width="300">
              <template #default="{ row }">
                <router-link :to="`/editor/${row.prompt_id}`" class="text-xs font-bold text-zinc-800 dark:text-zinc-200 hover:text-brand-accent transition-colors">
                  {{ row.title }}
                </router-link>
              </template>
            </el-table-column>
            <el-table-column prop="use_count" label="使用频率 USAGE" align="right">
              <template #default="{ row }">
                <span class="text-xs font-mono font-bold text-zinc-900 dark:text-white">{{ row.use_count }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="total_tokens" label="累计消耗 TOKENS" align="right">
              <template #default="{ row }">
                <span class="text-xs font-mono text-zinc-500">{{ formatNumber(row.total_tokens) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="total_cost" label="预估支出 COST" align="right">
              <template #default="{ row }">
                <span class="text-xs font-mono text-zinc-900 dark:text-white font-bold">${{ row.total_cost.toFixed(4) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="avg_response_time" label="平均延迟 LATENCY" align="right">
              <template #default="{ row }">
                <span class="text-xs font-mono text-zinc-500">{{ row.avg_response_time.toFixed(2) }}s</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { statisticsAPI, DailyStats, TopPrompt, ModelUsage } from '@/api'
import { Refresh, Connection, Coin, Money, Timer } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import * as echarts from 'echarts'

const selectedDays = ref(30)
const loading = ref(false)
const dailyChartType = ref<'calls' | 'tokens' | 'cost'>('calls')

const overview = reactive({ total_calls: 0, total_tokens: 0, total_input_tokens: 0, total_output_tokens: 0, total_cost: 0, avg_response_time: 0 })
const dailyStats = ref<DailyStats[]>([])
const topPrompts = ref<TopPrompt[]>([])
const modelUsage = ref<ModelUsage[]>([])
const hourlyData = ref<{ hours: number[]; calls: number[] }>({ hours: [], calls: [] })

const dailyChartRef = ref<HTMLElement>(); const modelChartRef = ref<HTMLElement>(); const hourlyChartRef = ref<HTMLElement>()
let dailyChart: echarts.ECharts | null = null; let modelChart: echarts.ECharts | null = null; let hourlyChart: echarts.ECharts | null = null

const overviewCards = computed(() => [
  { label: 'Total Calls', value: formatNumber(overview.total_calls), desc: '累计成功执行次数', icon: 'Connection' },
  { label: 'Token Consumption', value: formatNumber(overview.total_tokens), desc: '已消耗计算资源', icon: 'Coin' },
  { label: 'Projected Cost', value: `$${overview.total_cost.toFixed(2)}`, desc: '预估模型推理成本', icon: 'Money' },
  { label: 'Avg Latency', value: `${overview.avg_response_time.toFixed(2)}s`, desc: '模型端到端响应时间', icon: 'Timer' }
])

function formatNumber(num: number) { return num >= 1000000 ? (num / 1000000).toFixed(1) + 'M' : (num >= 1000 ? (num / 1000).toFixed(1) + 'K' : num.toString()) }

async function loadAllData() {
  loading.value = true
  try {
    const [ov, ds, tp, mu, hr] = await Promise.all([
      statisticsAPI.getOverview(selectedDays.value) as any,
      statisticsAPI.getDaily(selectedDays.value) as any,
      statisticsAPI.getTopPrompts({ days: selectedDays.value, limit: 10 }) as any,
      statisticsAPI.getModelUsage(selectedDays.value) as any,
      statisticsAPI.getHourly(Math.min(selectedDays.value, 30)) as any
    ])
    if (ov.data) Object.assign(overview, ov.data)
    dailyStats.value = ds.data || []; topPrompts.value = tp.data || []; modelUsage.value = mu.data || []; hourlyData.value = hr.data || { hours: [], calls: [] }
    await nextTick(); renderCharts()
  } finally { loading.value = false }
}

function getChartTheme() {
  const isDark = document.documentElement.classList.contains('dark')
  return {
    text: isDark ? '#94a3b8' : '#64748b',
    border: isDark ? '#1e293b' : '#f1f5f9',
    accent: isDark ? '#ffffff' : '#0f172a',
    grid: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)'
  }
}

function renderCharts() {
  const theme = getChartTheme()
  
  // Daily Chart
  if (dailyChartRef.value) {
    dailyChart = dailyChart || echarts.init(dailyChartRef.value)
    dailyChart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: '#0f172a', textStyle: { color: '#fff' }, borderWidth: 0, shadowBlur: 10 },
      grid: { left: '2%', right: '2%', bottom: '5%', top: '10%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: dailyStats.value.map(d => d.date.slice(5)), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: theme.text, fontSize: 10, margin: 15 } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: theme.grid } }, axisLabel: { color: theme.text, fontSize: 10 } },
      series: [{
        type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
        itemStyle: { color: theme.accent },
        lineStyle: { width: 3 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: theme.accent + '22' }, { offset: 1, color: theme.accent + '00' }]) },
        data: dailyStats.value.map(d => d[dailyChartType.value as keyof DailyStats])
      }]
    })
  }

  // Model Distribution
  if (modelChartRef.value) {
    modelChart = modelChart || echarts.init(modelChartRef.value)
    modelChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie', radius: ['60%', '85%'], center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 4, borderColor: theme.border, borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 12, fontWeight: 'bold', color: theme.accent } },
        data: modelUsage.value.map(m => ({ name: m.model, value: m.calls }))
      }],
      color: [theme.accent, '#3b82f6', '#10b981', '#f59e0b', '#6366f1']
    })
  }

  // Hourly Activity
  if (hourlyChartRef.value) {
    hourlyChart = hourlyChart || echarts.init(hourlyChartRef.value)
    hourlyChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '2%', right: '2%', bottom: '5%', top: '15%', containLabel: true },
      xAxis: { type: 'category', data: hourlyData.value.hours.map(h => `${h}h`), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: theme.text, fontSize: 9 } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: theme.grid } }, axisLabel: { color: theme.text, fontSize: 9 } },
      series: [{
        type: 'bar', barWidth: '60%', itemStyle: { color: theme.accent, borderRadius: [4, 4, 0, 0] },
        data: hourlyData.value.calls
      }]
    })
  }
}

watch(dailyChartType, () => renderCharts())
function handleResize() { dailyChart?.resize(); modelChart?.resize(); hourlyChart?.resize() }

onMounted(() => { loadAllData(); window.addEventListener('resize', handleResize) })
onUnmounted(() => { window.removeEventListener('resize', handleResize); dailyChart?.dispose(); modelChart?.dispose(); hourlyChart?.dispose() })
</script>

<style scoped>
.studio-select-minimal :deep(.el-input__wrapper) {
  @apply bg-white dark:bg-zinc-900 !shadow-none border border-zinc-200 dark:border-zinc-800 rounded-lg h-10 px-3 transition-all;
}

:deep(.studio-table) {
  --el-table-header-bg-color: transparent;
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-border-color: #f1f5f9;
}

.dark :deep(.studio-table) {
  --el-table-border-color: #1e293b;
}

:deep(.el-table th.el-table__cell) {
  @apply text-[9px] font-black uppercase tracking-widest text-zinc-400 py-4;
}

:deep(.el-table td.el-table__cell) {
  @apply py-4;
}

.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
