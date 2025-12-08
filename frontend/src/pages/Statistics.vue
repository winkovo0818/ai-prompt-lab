<template>
  <div class="statistics-page">
    <Header />
    
    <div class="page-content">
      <div class="page-header">
        <h1>使用统计</h1>
        <div class="header-actions">
          <el-select v-model="selectedDays" @change="loadAllData" style="width: 140px">
            <el-option :value="7" label="最近 7 天" />
            <el-option :value="14" label="最近 14 天" />
            <el-option :value="30" label="最近 30 天" />
            <el-option :value="90" label="最近 90 天" />
          </el-select>
          <el-button @click="loadAllData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <!-- 概览卡片 -->
      <div class="overview-cards" v-loading="loading">
        <div class="stat-card">
          <div class="stat-icon calls">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(overview.total_calls) }}</div>
            <div class="stat-label">API 调用次数</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon tokens">
            <el-icon><Coin /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(overview.total_tokens) }}</div>
            <div class="stat-label">Token 消耗</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon cost">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">${{ overview.total_cost.toFixed(4) }}</div>
            <div class="stat-label">预估成本</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon time">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overview.avg_response_time.toFixed(2) }}s</div>
            <div class="stat-label">平均响应时间</div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <!-- 每日趋势图 -->
        <div class="chart-card large">
          <div class="chart-header">
            <h3>每日调用趋势</h3>
            <el-radio-group v-model="dailyChartType" size="small">
              <el-radio-button value="calls">调用量</el-radio-button>
              <el-radio-button value="tokens">Token</el-radio-button>
              <el-radio-button value="cost">成本</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container" ref="dailyChartRef"></div>
        </div>

        <!-- 模型使用分布 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>模型使用分布</h3>
          </div>
          <div class="chart-container" ref="modelChartRef"></div>
        </div>

        <!-- 每小时调用分布 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>24 小时调用分布</h3>
          </div>
          <div class="chart-container" ref="hourlyChartRef"></div>
        </div>
      </div>

      <!-- 最常用 Prompt -->
      <div class="top-prompts-section">
        <div class="section-header">
          <h3>最常用的 Prompt</h3>
        </div>
        <el-table :data="topPrompts" v-loading="loading" stripe>
          <el-table-column prop="title" label="Prompt 标题" min-width="200">
            <template #default="{ row }">
              <router-link :to="`/editor/${row.prompt_id}`" class="prompt-link">
                {{ row.title }}
              </router-link>
            </template>
          </el-table-column>
          <el-table-column prop="use_count" label="使用次数" width="120" align="center">
            <template #default="{ row }">
              <el-tag type="primary">{{ row.use_count }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_tokens" label="Token 消耗" width="120" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.total_tokens) }}
            </template>
          </el-table-column>
          <el-table-column prop="total_cost" label="成本" width="100" align="right">
            <template #default="{ row }">
              ${{ row.total_cost.toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column prop="avg_response_time" label="平均响应" width="120" align="right">
            <template #default="{ row }">
              {{ row.avg_response_time.toFixed(2) }}s
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && topPrompts.length === 0" description="暂无使用记录" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { statisticsAPI, DailyStats, TopPrompt, ModelUsage } from '@/api'
import { ElMessage } from 'element-plus'
import { Refresh, Connection, Coin, Money, Timer } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'
import * as echarts from 'echarts'

const selectedDays = ref(30)
const loading = ref(false)
const dailyChartType = ref<'calls' | 'tokens' | 'cost'>('calls')

const overview = reactive({
  total_calls: 0,
  total_tokens: 0,
  total_input_tokens: 0,
  total_output_tokens: 0,
  total_cost: 0,
  avg_response_time: 0
})

const dailyStats = ref<DailyStats[]>([])
const topPrompts = ref<TopPrompt[]>([])
const modelUsage = ref<ModelUsage[]>([])
const hourlyData = ref<{ hours: number[]; calls: number[] }>({ hours: [], calls: [] })

// 图表引用
const dailyChartRef = ref<HTMLElement>()
const modelChartRef = ref<HTMLElement>()
const hourlyChartRef = ref<HTMLElement>()

let dailyChart: echarts.ECharts | null = null
let modelChart: echarts.ECharts | null = null
let hourlyChart: echarts.ECharts | null = null

// 格式化数字
function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

// 加载所有数据
async function loadAllData() {
  loading.value = true
  try {
    await Promise.all([
      loadOverview(),
      loadDailyStats(),
      loadTopPrompts(),
      loadModelUsage(),
      loadHourlyStats()
    ])
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadOverview() {
  const response = await statisticsAPI.getOverview(selectedDays.value) as any
  if (response.data) {
    Object.assign(overview, response.data)
  }
}

async function loadDailyStats() {
  const response = await statisticsAPI.getDaily(selectedDays.value) as any
  if (response.data) {
    dailyStats.value = response.data
    await nextTick()
    renderDailyChart()
  }
}

async function loadTopPrompts() {
  const response = await statisticsAPI.getTopPrompts({ 
    days: selectedDays.value, 
    limit: 10 
  }) as any
  if (response.data) {
    topPrompts.value = response.data
  }
}

async function loadModelUsage() {
  const response = await statisticsAPI.getModelUsage(selectedDays.value) as any
  if (response.data) {
    modelUsage.value = response.data
    await nextTick()
    renderModelChart()
  }
}

async function loadHourlyStats() {
  const response = await statisticsAPI.getHourly(Math.min(selectedDays.value, 30)) as any
  if (response.data) {
    hourlyData.value = response.data
    await nextTick()
    renderHourlyChart()
  }
}

// 渲染每日趋势图
function renderDailyChart() {
  if (!dailyChartRef.value) return
  
  if (!dailyChart) {
    dailyChart = echarts.init(dailyChartRef.value)
  }
  
  const dataKey = dailyChartType.value
  const labelMap: Record<string, string> = {
    calls: '调用次数',
    tokens: 'Token 消耗',
    cost: '成本 ($)'
  }
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dailyStats.value.map(d => d.date),
      axisLabel: {
        formatter: (value: string) => value.slice(5) // 只显示月-日
      }
    },
    yAxis: {
      type: 'value',
      name: labelMap[dataKey]
    },
    series: [{
      name: labelMap[dataKey],
      type: 'line',
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      data: dailyStats.value.map(d => d[dataKey as keyof DailyStats]),
      itemStyle: {
        color: dataKey === 'calls' ? '#409eff' : dataKey === 'tokens' ? '#67c23a' : '#e6a23c'
      }
    }]
  }
  
  dailyChart.setOption(option)
}

// 渲染模型使用分布图
function renderModelChart() {
  if (!modelChartRef.value) return
  
  if (!modelChart) {
    modelChart = echarts.init(modelChartRef.value)
  }
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      data: modelUsage.value.map(m => ({
        name: m.model,
        value: m.calls
      }))
    }]
  }
  
  modelChart.setOption(option)
}

// 渲染每小时分布图
function renderHourlyChart() {
  if (!hourlyChartRef.value) return
  
  if (!hourlyChart) {
    hourlyChart = echarts.init(hourlyChartRef.value)
  }
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}:00 - {c} 次调用'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hourlyData.value.hours.map(h => `${h}:00`),
      axisLabel: {
        interval: 2
      }
    },
    yAxis: {
      type: 'value',
      name: '调用次数'
    },
    series: [{
      type: 'bar',
      data: hourlyData.value.calls,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#188df0' }
        ])
      }
    }]
  }
  
  hourlyChart.setOption(option)
}

// 监听图表类型变化
watch(dailyChartType, () => {
  renderDailyChart()
})

// 窗口大小变化时重绘图表
function handleResize() {
  dailyChart?.resize()
  modelChart?.resize()
  hourlyChart?.resize()
}

onMounted(() => {
  loadAllData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  dailyChart?.dispose()
  modelChart?.dispose()
  hourlyChart?.dispose()
})
</script>

<style scoped>
.statistics-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* 概览卡片 */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon.calls {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.tokens {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
}

.stat-icon.cost {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.time {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 0.25rem;
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-card.large {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1e293b;
}

.chart-container {
  height: 280px;
}

.chart-card.large .chart-container {
  height: 320px;
}

/* 最常用 Prompt */
.top-prompts-section {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  margin-bottom: 1rem;
}

.section-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1e293b;
}

.prompt-link {
  color: #409eff;
  text-decoration: none;
}

.prompt-link:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 1200px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .chart-card.large {
    grid-column: auto;
  }
}

@media (max-width: 768px) {
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>
