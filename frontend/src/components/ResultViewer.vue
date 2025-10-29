<template>
  <div class="result-viewer">
    <div class="header flex items-center justify-between mb-4">
      <h4 class="text-sm font-semibold text-gray-700">执行结果</h4>
      <div class="actions flex space-x-2">
        <el-button 
          text 
          @click="copyResult" 
          :icon="copied ? 'Check' : 'CopyDocument'"
          size="small"
        >
          {{ copied ? '已复制' : '复制' }}
        </el-button>
        <el-button 
          text 
          @click="downloadResult"
          icon="Download"
          size="small"
        >
          下载
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="result" class="result-content">
      <!-- 缓存标识 -->
      <div v-if="result.is_cached" class="cache-banner">
        <el-alert 
          type="info" 
          :closable="false"
        >
          <template #title>
            <span>使用历史执行结果（未调用AI）</span>
          </template>
          <div>
            这是之前执行的结果，节省了API调用成本
            <span v-if="result.cached_at" class="cache-time">
              · {{ formatCacheTime(result.cached_at) }}
            </span>
          </div>
        </el-alert>
      </div>

      <!-- 统计信息卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon model-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">模型</div>
            <div class="stat-value">{{ result.model }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon token-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">Token 用量</div>
            <div class="stat-value">{{ result.total_tokens }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon time-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">响应时间</div>
            <div class="stat-value">{{ result.response_time }}s</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon cost-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">调用成本</div>
            <div class="stat-value">{{ formatCost(result.cost) }}</div>
          </div>
        </div>
      </div>

      <!-- 输出内容区域 -->
      <div class="output-section">
        <div class="section-header">
          <div class="section-title">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <span>输出结果</span>
          </div>
          <el-button 
            type="primary"
            @click="showRenderedDialog"
            :icon="View"
            size="default"
          >
            详情
          </el-button>
        </div>
        
        <div class="output-wrapper">
          <div class="output-text">{{ result.output }}</div>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state text-center py-12 text-gray-400">
      <el-icon :size="48"><Document /></el-icon>
      <p class="mt-4">暂无结果</p>
    </div>
    
    <!-- 渲染视图弹框 -->
    <el-dialog
      v-model="renderedDialogVisible"
      title="详情"
      width="90%"
      top="5vh"
      :close-on-click-modal="false"
    >
      <div class="rendered-dialog-content">
        <div 
          class="markdown-body"
          v-html="renderedOutput"
        ></div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="copyResult" :icon="copied ? Check : CopyDocument">
            {{ copied ? '已复制' : '复制内容' }}
          </el-button>
          <el-button @click="downloadResult" :icon="Download">
            下载
          </el-button>
          <el-button type="primary" @click="renderedDialogVisible = false">
            关闭
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { renderMarkdown } from '@/utils/markdown'
import { formatCost } from '@/utils/format'
import { ElMessage } from 'element-plus'
import { Document, View, CopyDocument, Check, Download } from '@element-plus/icons-vue'

const props = defineProps<{
  result?: any
  loading?: boolean
  autoShowRendered?: boolean
}>()

const renderedDialogVisible = ref(false)
const copied = ref(false)

const renderedOutput = computed(() => {
  if (!props.result?.output) return ''
  return renderMarkdown(props.result.output)
})

// 监听autoShowRendered，自动打开渲染视图弹框
watch(() => props.autoShowRendered, (newVal) => {
  if (newVal && props.result) {
    renderedDialogVisible.value = true
  }
}, { immediate: true })

function showRenderedDialog() {
  renderedDialogVisible.value = true
}

async function copyResult() {
  if (!props.result?.output) return

  try {
    await navigator.clipboard.writeText(props.result.output)
    copied.value = true
    ElMessage.success('已复制到剪贴板')
    
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

function downloadResult() {
  if (!props.result?.output) return

  const blob = new Blob([props.result.output], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `result-${Date.now()}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)

  ElMessage.success('下载成功')
}

function formatCacheTime(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  // 小于1分钟
  if (diff < 60 * 1000) {
    return '刚刚'
  }
  
  // 小于1小时
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000))
    return `${minutes}分钟前`
  }
  
  // 小于24小时
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    return `${hours}小时前`
  }
  
  // 小于7天
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000))
    return `${days}天前`
  }
  
  // 格式化为标准日期时间
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
}
</script>

<style scoped>
.result-viewer {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
}

.cache-banner {
  margin-bottom: 0;
}

.cache-banner :deep(.el-alert) {
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.cache-time {
  color: #6b7280;
  font-size: 0.875rem;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.model-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  color: #0284c7;
}

.token-icon {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  color: #16a34a;
}

.time-icon {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.cost-icon {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  color: #db2777;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 输出区域 */
.output-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #fafafa;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.section-title svg {
  width: 20px;
  height: 20px;
  color: #3b82f6;
}

.section-header .el-button--primary {
  background: #3b82f6;
  border-color: #3b82f6;
}

.section-header .el-button--primary:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.output-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.output-text {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9375rem;
  line-height: 1.7;
  color: #374151;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  min-height: 200px;
}

.markdown-body {
  max-width: 900px;
  margin: 0 auto;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  min-height: 400px;
  box-sizing: border-box;
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
}

/* 标题样式优化 */
.markdown-body :deep(h1) {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin-top: 2rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
  line-height: 1.3;
}

.markdown-body :deep(h2) {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.markdown-body :deep(h3) {
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.markdown-body :deep(h4) {
  font-size: 1.125rem;
  font-weight: 600;
  color: #4b5563;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}

/* 段落样式 */
.markdown-body :deep(p) {
  margin-bottom: 1.5rem;
  line-height: 1.8;
  color: #4a5568;
}

/* 列表样式 */
.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin-bottom: 1.5rem;
  padding-left: 2rem;
}

.markdown-body :deep(li) {
  margin-bottom: 0.75rem;
  line-height: 1.8;
  color: #4a5568;
}

.markdown-body :deep(li > p) {
  margin-bottom: 0.5rem;
}

/* 代码块样式增强 */
.markdown-body :deep(pre) {
  background: #1f2937 !important;
  border-radius: 6px;
  padding: 1rem !important;
  overflow-x: auto;
  margin: 1rem 0 !important;
  border: 1px solid #374151;
}

.markdown-body :deep(pre code) {
  background: transparent !important;
  color: #e5e7eb !important;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}

/* 内联代码样式 */
.markdown-body :deep(code:not(pre code)) {
  background: #f3f4f6;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.875em;
  color: #dc2626;
  border: 1px solid #e5e7eb;
}

/* 链接样式优化 */
.markdown-body :deep(a) {
  color: #3b82f6;
  text-decoration: none;
  transition: color 0.2s ease;
}

.markdown-body :deep(a:hover) {
  color: #2563eb;
  text-decoration: underline;
}

/* 引用块样式优化 */
.markdown-body :deep(blockquote) {
  border-left: 4px solid #d1d5db;
  background: #f9fafb;
  padding: 1rem 1.5rem;
  margin: 1rem 0;
  color: #4b5563;
}

.markdown-body :deep(blockquote p) {
  margin-bottom: 0.5rem;
}

.markdown-body :deep(blockquote p:last-child) {
  margin-bottom: 0;
}

/* 分隔线 */
.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 2rem 0;
}

/* 表格样式优化 */
.markdown-body :deep(table) {
  border-collapse: collapse;
  border-spacing: 0;
  margin: 1rem 0;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.markdown-body :deep(th) {
  background: #f9fafb;
  color: #374151;
  font-weight: 600;
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.875rem;
}

.markdown-body :deep(td) {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #4b5563;
}

.markdown-body :deep(tr:last-child td) {
  border-bottom: none;
}

.markdown-body :deep(tbody tr:hover) {
  background: #f9fafb;
}

/* 强调样式 */
.markdown-body :deep(strong) {
  font-weight: 700;
  color: #2d3748;
}

.markdown-body :deep(em) {
  font-style: italic;
  color: #718096;
}


/* 弹框样式 */
.rendered-dialog-content {
  max-height: 75vh;
  overflow-y: auto;
  padding: 2rem;
  background: #f9fafb;
}

.rendered-dialog-content .markdown-body {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.dialog-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

:deep(.el-dialog) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

:deep(.el-dialog__header) {
  padding: 1.5rem 2rem;
  margin: 0;
  border-bottom: 1px solid #e5e7eb;
  background: white;
}

:deep(.el-dialog__title) {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

:deep(.el-dialog__headerbtn) {
  top: 1.5rem;
  right: 2rem;
}

:deep(.el-dialog__close) {
  color: #6b7280;
  font-size: 1.25rem;
}

:deep(.el-dialog__close:hover) {
  color: #374151;
}

:deep(.el-dialog__body) {
  padding: 0;
  background: #f9fafb;
}

:deep(.el-dialog__footer) {
  padding: 1rem 2rem;
  border-top: 1px solid #e5e7eb;
  background: white;
}

:deep(.el-dialog__footer .el-button) {
  padding: 0.5rem 1rem;
  font-size: 14px;
  border-radius: 6px;
}

:deep(.el-dialog__footer .el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}

:deep(.el-dialog__footer .el-button--primary:hover) {
  background: #2563eb;
  border-color: #2563eb;
}

.loading-state,
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.cache-banner :deep(.el-alert) {
  background: linear-gradient(to right, #e0f2fe, #dbeafe);
  border-color: #3b82f6;
}

.cache-banner :deep(.el-alert__title) {
  color: #1e40af;
}

.cache-banner :deep(.el-alert__description) {
  color: #1e3a8a;
}
</style>

