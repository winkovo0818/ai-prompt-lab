<template>
  <div class="prompt-editor-page">
    <Header />
    
    <div class="editor-container">
      <div class="editor-main">
        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
              <span class="text-gray-400">|</span>
              <span class="text-sm text-gray-600">
                {{ isEditMode ? '编辑 Prompt' : '新建 Prompt' }}
              </span>
              <el-tag v-if="teamShared && teamInfo" type="primary" size="small" class="ml-2">
                来自: {{ teamInfo.team_name }}
              </el-tag>
              <el-tag v-if="teamShared && !canEdit" type="warning" size="small">
                只读
              </el-tag>
            </div>

            <div class="flex items-center space-x-2">
              <el-button 
                v-if="isEditMode" 
                @click="showExecutionHistory" 
                icon="List"
              >
                执行历史
              </el-button>
              <el-button 
                v-if="isEditMode" 
                @click="showVersionHistory" 
                icon="Clock"
              >
                版本历史
              </el-button>
              <el-button 
                v-if="isEditMode && isOwner" 
                @click="handleDelete" 
                type="danger"
                icon="Delete"
              >
                删除
              </el-button>
              <el-button 
                @click="handleSave" 
                type="primary" 
                :loading="saving"
                :disabled="!canEdit"
                :title="canEdit ? 'Ctrl+S' : '没有编辑权限'"
              >
                <el-icon><DocumentChecked /></el-icon>
                保存
              </el-button>
              <el-dropdown split-button type="success" @click="handleRun" :loading="running" title="Ctrl+Enter">
                <el-icon><CaretRight /></el-icon>
                运行
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="showMultiModelDialog">
                      <el-icon><Operation /></el-icon>
                      多模型对比
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>

        <!-- 只读提示 -->
        <div v-if="teamShared && !canEdit" class="readonly-banner">
          <el-icon><InfoFilled /></el-icon>
          <span>此 Prompt 来自团队 <strong>{{ teamInfo?.team_name }}</strong>，您只有查看权限</span>
        </div>

        <!-- 编辑区域 -->
        <div class="editor-content">
          <div class="editor-left">
            <div class="form-section">
              <el-form :model="formData" label-position="top">
                <el-form-item label="标题">
                  <el-input
                    v-model="formData.title"
                    placeholder="给你的 Prompt 起个名字"
                    size="large"
                    :disabled="!canEdit"
                  />
                </el-form-item>

                <el-form-item label="描述">
                  <el-input
                    v-model="formData.description"
                    type="textarea"
                    :rows="2"
                    placeholder="简单描述一下这个 Prompt 的用途"
                    :disabled="!canEdit"
                  />
                </el-form-item>

                <el-form-item label="Prompt 内容">
                  <PromptCodeEditor
                    v-model="formData.content"
                    placeholder="输入你的 Prompt，使用 {{变量名}} 来添加变量"
                    :rows="15"
                    :disabled="!canEdit"
                    @input="handleContentChange"
                  />
                </el-form-item>

                <el-form-item label="标签">
                  <el-select
                    v-model="formData.tags"
                    multiple
                    filterable
                    allow-create
                    placeholder="添加标签"
                    class="w-full"
                    :disabled="!canEdit"
                  >
                    <el-option
                      v-for="tag in commonTags"
                      :key="tag"
                      :label="tag"
                      :value="tag"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item>
                  <el-checkbox v-model="formData.is_public" :disabled="!canEdit">
                    公开分享（其他人可以查看）
                  </el-checkbox>
                </el-form-item>
              </el-form>
            </div>
          </div>

          <div class="editor-right">
            <el-tabs v-model="activeTab" class="h-full">
              <el-tab-pane label="变量配置" name="variables">
                <VariableInputWithFile
                  :variables="variables"
                  :content="formData.content"
                  v-model="variableValues"
                  v-model:file-model-value="fileVariableValues"
                />
              </el-tab-pane>

              <el-tab-pane label="执行结果" name="result">
                <ResultViewer
                  :result="executionResult"
                  :loading="running"
                  :auto-show-rendered="autoShowRendered"
                />
              </el-tab-pane>

              <el-tab-pane label="模型配置" name="settings">
                <div class="settings-panel">
                  <el-form label-position="top">
                    <el-form-item label="模型">
                      <el-select v-model="configStore.selectedModel" class="w-full">
                        <el-option
                          v-for="model in configStore.availableModels"
                          :key="model.id"
                          :label="model.name"
                          :value="model.id"
                        >
                          <div>
                            <div>{{ model.name }}</div>
                            <div class="text-xs text-gray-500">{{ model.description }}</div>
                          </div>
                        </el-option>
                      </el-select>
                    </el-form-item>

                    <el-form-item label="Temperature">
                      <el-slider
                        v-model="configStore.temperature"
                        :min="0"
                        :max="2"
                        :step="0.1"
                        show-input
                      />
                    </el-form-item>

                    <el-form-item label="Max Tokens">
                      <el-input-number
                        v-model="configStore.maxTokens"
                        :min="100"
                        :max="128000"
                        :step="100"
                        class="w-full"
                      />
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>

              <el-tab-pane label="智能分析" name="analysis">
                <div class="analysis-panel">
                  <!-- 分析按钮 -->
                  <div class="analysis-actions">
                    <el-button 
                      type="primary" 
                      @click="handleAnalyze" 
                      :loading="analyzing"
                      :disabled="!formData.content"
                    >
                      <el-icon><MagicStick /></el-icon>
                      AI 深度分析
                    </el-button>
                    <el-button 
                      @click="handleQuickAnalyze"
                      :disabled="!formData.content"
                    >
                      快速检查
                    </el-button>
                  </div>

                  <!-- 快速分析结果 -->
                  <div v-if="quickAnalysis" class="quick-analysis">
                    <div class="quick-score">
                      <el-progress 
                        type="circle" 
                        :percentage="quickAnalysis.quick_score"
                        :color="getScoreColor(quickAnalysis.quick_score)"
                        :width="80"
                      />
                      <span class="score-label">快速评分</span>
                    </div>
                    <div class="quick-stats">
                      <div class="stat-item">
                        <span class="stat-label">字符数</span>
                        <span class="stat-value">{{ quickAnalysis.character_count }}</span>
                      </div>
                      <div class="stat-item">
                        <span class="stat-label">变量数</span>
                        <span class="stat-value">{{ quickAnalysis.variable_count }}</span>
                      </div>
                      <div class="stat-item">
                        <el-tag :type="quickAnalysis.has_role ? 'success' : 'info'" size="small">
                          {{ quickAnalysis.has_role ? '有角色设定' : '无角色设定' }}
                        </el-tag>
                      </div>
                      <div class="stat-item">
                        <el-tag :type="quickAnalysis.has_format ? 'success' : 'info'" size="small">
                          {{ quickAnalysis.has_format ? '有格式要求' : '无格式要求' }}
                        </el-tag>
                      </div>
                    </div>
                    <div class="quick-tips" v-if="quickAnalysis.tips?.length">
                      <div 
                        v-for="(tip, index) in quickAnalysis.tips" 
                        :key="index"
                        :class="['tip-item', `tip-${tip.type}`]"
                      >
                        <el-icon v-if="tip.type === 'warning'"><Warning /></el-icon>
                        <el-icon v-else-if="tip.type === 'suggestion'"><InfoFilled /></el-icon>
                        <el-icon v-else><CircleCheck /></el-icon>
                        <span>{{ tip.message }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- AI 深度分析结果 -->
                  <div v-if="analysisResult" class="ai-analysis">
                    <div class="analysis-header">
                      <el-divider>AI 分析报告</el-divider>
                      <el-button size="small" @click="downloadReport" class="download-btn">
                        <el-icon><Download /></el-icon>
                        下载报告
                      </el-button>
                    </div>
                    
                    <!-- 总分 -->
                    <div class="overall-score">
                      <el-progress 
                        type="dashboard" 
                        :percentage="analysisResult.overall_score"
                        :color="getScoreColor(analysisResult.overall_score)"
                        :width="120"
                      >
                        <template #default>
                          <span class="score-number">{{ analysisResult.overall_score }}</span>
                          <span class="score-text">总分</span>
                        </template>
                      </el-progress>
                    </div>

                    <!-- 维度评分 -->
                    <div class="dimensions">
                      <div class="dimension-item" v-for="(dim, key) in analysisResult.dimensions" :key="key">
                        <div class="dim-header">
                          <span class="dim-name">{{ getDimensionName(key) }}</span>
                          <span class="dim-score">{{ dim.score }}</span>
                        </div>
                        <el-progress 
                          :percentage="dim.score" 
                          :color="getScoreColor(dim.score)"
                          :stroke-width="8"
                        />
                        <div class="dim-comment">{{ dim.comment }}</div>
                      </div>
                    </div>

                    <!-- 优缺点 -->
                    <div class="strengths-weaknesses">
                      <div class="sw-section strengths" v-if="analysisResult.strengths?.length">
                        <h4><el-icon><CircleCheckFilled /></el-icon> 优点</h4>
                        <ul>
                          <li v-for="(s, i) in analysisResult.strengths" :key="i">{{ s }}</li>
                        </ul>
                      </div>
                      <div class="sw-section weaknesses" v-if="analysisResult.weaknesses?.length">
                        <h4><el-icon><WarningFilled /></el-icon> 待改进</h4>
                        <ul>
                          <li v-for="(w, i) in analysisResult.weaknesses" :key="i">{{ w }}</li>
                        </ul>
                      </div>
                    </div>

                    <!-- 改进建议 -->
                    <div class="suggestions" v-if="analysisResult.suggestions?.length">
                      <h4>改进建议</h4>
                      <el-collapse>
                        <el-collapse-item 
                          v-for="(sug, i) in analysisResult.suggestions" 
                          :key="i"
                          :name="i"
                        >
                          <template #title>
                            <el-tag 
                              :type="sug.priority === 'high' ? 'danger' : sug.priority === 'medium' ? 'warning' : 'info'" 
                              size="small"
                            >
                              {{ sug.priority === 'high' ? '高优先' : sug.priority === 'medium' ? '中优先' : '建议' }}
                            </el-tag>
                            <span class="sug-title">{{ sug.title }}</span>
                          </template>
                          <div class="sug-content">
                            <p>{{ sug.description }}</p>
                            <div v-if="sug.example" class="sug-example">
                              <strong>示例：</strong>
                              <pre>{{ sug.example }}</pre>
                            </div>
                          </div>
                        </el-collapse-item>
                      </el-collapse>
                    </div>

                    <!-- 最佳实践检查 -->
                    <div class="best-practices" v-if="analysisResult.best_practices?.length">
                      <h4>最佳实践检查</h4>
                      <div class="practice-list">
                        <div 
                          v-for="(bp, i) in analysisResult.best_practices" 
                          :key="i"
                          :class="['practice-item', bp.status]"
                        >
                          <el-icon v-if="bp.status === 'pass'"><CircleCheckFilled /></el-icon>
                          <el-icon v-else><CircleCloseFilled /></el-icon>
                          <span class="practice-rule">{{ bp.rule }}</span>
                          <span class="practice-msg">{{ bp.message }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- 优化后的 Prompt -->
                    <div class="optimized-prompt" v-if="analysisResult.optimized_prompt">
                      <h4>优化后的 Prompt</h4>
                      <div class="optimized-content">
                        <pre>{{ analysisResult.optimized_prompt }}</pre>
                        <el-button 
                          size="small" 
                          type="primary"
                          @click="applyOptimizedPrompt"
                        >
                          应用此版本
                        </el-button>
                      </div>
                    </div>
                  </div>

                  <!-- 空状态 -->
                  <el-empty 
                    v-if="!quickAnalysis && !analysisResult && !analyzing" 
                    description="点击上方按钮分析你的 Prompt"
                  />
                </div>
              </el-tab-pane>

              <el-tab-pane label="评论" name="comments" v-if="isEditMode">
                <PromptComments 
                  :prompt-id="Number(route.params.id)"
                  :versions="versionNumbers"
                  :is-owner="isOwner"
                />
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </div>

    <!-- 版本历史抽屉 -->
    <el-drawer
      v-model="versionDrawerVisible"
      title="版本历史"
      direction="rtl"
      size="600px"
    >
      <div class="version-history-container">
        <el-timeline v-if="versions.length > 0">
          <el-timeline-item
            v-for="version in versions"
            :key="version.id"
            :timestamp="formatDate(version.created_at)"
            placement="top"
          >
            <el-card shadow="hover" class="version-card">
              <div class="version-header">
                <div class="version-info">
                  <span class="version-number">版本 {{ version.version }}</span>
                  <el-tag size="small" type="info" v-if="version.version === currentVersion">
                    当前版本
                  </el-tag>
                </div>
                <div class="version-actions">
                  <el-button 
                    size="small" 
                    @click="viewVersionContent(version)"
                    icon="View"
                  >
                    查看
                  </el-button>
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="restoreVersion(version)"
                    :disabled="version.version === currentVersion"
                    icon="RefreshLeft"
                  >
                    恢复
                  </el-button>
                </div>
              </div>
              <div class="version-summary">
                <div class="version-title">{{ version.title }}</div>
                <div class="version-change" v-if="version.change_summary">
                  变更：{{ version.change_summary }}
                </div>
                <div class="version-meta">
                  内容长度：{{ version.content.length }} 字符
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        
        <el-empty v-else description="暂无版本历史" />
      </div>
    </el-drawer>

    <!-- 版本内容查看对话框 -->
    <el-dialog
      v-model="versionContentVisible"
      :title="`版本 ${selectedVersion?.version} - ${selectedVersion?.title}`"
      width="80%"
      top="5vh"
    >
      <div v-if="selectedVersion" class="version-content-detail">
        <div class="version-meta-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="版本号">
              {{ selectedVersion.version }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(selectedVersion.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="标题" :span="2">
              {{ selectedVersion.title }}
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">
              {{ selectedVersion.description || '无' }}
            </el-descriptions-item>
            <el-descriptions-item label="变更摘要" :span="2">
              {{ selectedVersion.change_summary || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="version-content-preview">
          <h4>Prompt 内容</h4>
          <div class="content-box">
            <pre>{{ selectedVersion.content }}</pre>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="versionContentVisible = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="restoreVersion(selectedVersion!)"
          :disabled="selectedVersion?.version === currentVersion"
        >
          恢复到此版本
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行历史抽屉 -->
    <el-drawer
      v-model="executionHistoryDrawerVisible"
      title="执行历史"
      direction="rtl"
      size="700px"
    >
      <div class="execution-history-container">
        <div v-if="executionHistoryList.length > 0" class="history-list">
          <el-card 
            v-for="history in executionHistoryList" 
            :key="history.id"
            shadow="hover"
            class="history-card"
          >
            <div class="history-header">
              <div class="history-time">
                <el-icon><Clock /></el-icon>
                <span>{{ formatDate(history.created_at) }}</span>
              </div>
              <el-button 
                size="small" 
                type="primary"
                @click="viewExecutionHistory(history)"
              >
                查看结果
              </el-button>
            </div>
            
            <div class="history-info">
              <div class="info-row">
                <span class="label">模型:</span>
                <span class="value">{{ history.model }}</span>
              </div>
              <div class="info-row">
                <span class="label">Token:</span>
                <span class="value">{{ history.total_tokens }}</span>
              </div>
              <div class="info-row">
                <span class="label">成本:</span>
                <span class="value">${{ history.cost.toFixed(4) }}</span>
              </div>
              <div class="info-row">
                <span class="label">响应时间:</span>
                <span class="value">{{ history.response_time }}s</span>
              </div>
              <div v-if="history.variables && Object.keys(history.variables).length > 0" class="info-row">
                <span class="label">变量:</span>
                <span class="value">{{ JSON.stringify(history.variables) }}</span>
              </div>
            </div>
          </el-card>
        </div>
        
        <el-empty v-else description="暂无执行历史" />
      </div>
    </el-drawer>

    <!-- 多模型测试对话框 -->
    <el-dialog v-model="multiModelDialogVisible" title="多模型对比测试" width="900px" top="5vh">
      <div class="multi-model-dialog">
        <div class="model-selection">
          <div class="selection-header">
            <span class="title">选择要对比的模型</span>
            <span class="subtitle">至少选择 2 个模型</span>
          </div>
          <div class="model-grid">
            <div 
              v-for="model in configStore.availableModels" 
              :key="model.id"
              class="model-card"
              :class="{ selected: selectedModels.includes(model.id) }"
              @click="toggleModel(model.id)"
            >
              <el-checkbox 
                :model-value="selectedModels.includes(model.id)"
                @click.stop
                @change="toggleModel(model.id)"
              />
              <div class="model-info">
                <div class="model-name">{{ model.name }}</div>
                <div class="model-desc">{{ model.description || model.provider }}</div>
              </div>
            </div>
          </div>
          <div class="selection-status">
            已选择 <strong>{{ selectedModels.length }}</strong> 个模型
          </div>
        </div>
        
        <!-- 测试结果 -->
        <div v-if="multiModelResults.length > 0" class="multi-model-results">
          <el-divider content-position="left">
            <el-icon><DataAnalysis /></el-icon>
            对比结果
          </el-divider>
          
          <!-- 统计对比表 -->
          <div class="compare-stats-table">
            <el-table :data="multiModelResults" stripe size="small">
              <el-table-column prop="model" label="模型" width="180">
                <template #default="{ row }">
                  <div class="model-cell">
                    <el-tag :type="row.success ? 'primary' : 'danger'" size="small">
                      {{ row.model }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-icon v-if="row.success" color="#67c23a"><CircleCheckFilled /></el-icon>
                  <el-icon v-else color="#f56c6c"><CircleCloseFilled /></el-icon>
                </template>
              </el-table-column>
              <el-table-column label="耗时" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.success">{{ row.time.toFixed(2) }}s</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="Token" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.success">{{ row.data?.total_tokens }}</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="成本" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.success">${{ row.data?.cost?.toFixed(4) }}</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 输出对比 -->
          <div class="compare-outputs">
            <div 
              v-for="result in multiModelResults" 
              :key="result.model" 
              class="output-panel"
            >
              <div class="output-header">
                <span class="output-model">{{ result.model }}</span>
                <el-tag v-if="result.success" type="success" size="small">成功</el-tag>
                <el-tag v-else type="danger" size="small">失败</el-tag>
              </div>
              <div v-if="result.success" class="output-content">
                <ResultViewer :result="{ output: result.data?.output }" />
              </div>
              <div v-else class="output-error">
                <el-icon><WarningFilled /></el-icon>
                {{ result.error }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="multiModelDialogVisible = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="runMultiModelTest" 
          :loading="multiModelRunning"
          :disabled="selectedModels.length < 2"
        >
          开始测试
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePromptStore } from '@/store/prompt'
import { useConfigStore } from '@/store/config'
import { runAPI, promptAPI, executionHistoryAPI, promptAnalysisAPI, PromptAnalysisResult, QuickAnalysisResult } from '@/api'
import { MagicStick, Warning, InfoFilled, CircleCheck, CircleCheckFilled, WarningFilled, CircleCloseFilled, Download, Operation, DataAnalysis } from '@element-plus/icons-vue'
import { extractVariables } from '@/utils/markdown'
import { ElMessage, ElMessageBox } from 'element-plus'
import Header from '@/components/Layout/Header.vue'
import VariableInputWithFile from '@/components/VariableInputWithFile.vue'
import ResultViewer from '@/components/ResultViewer.vue'
import PromptComments from '@/components/PromptComments.vue'
import PromptCodeEditor from '@/components/PromptCodeEditor.vue'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const promptStore = usePromptStore()
const configStore = useConfigStore()
const userStore = useUserStore()

const activeTab = ref('variables')
const saving = ref(false)
const running = ref(false)

const formData = reactive({
  title: '',
  content: '',
  description: '',
  tags: [] as string[],
  is_public: false
})

const variableValues = ref<Record<string, string>>({})
const fileVariableValues = ref<Record<string, number>>({})
const executionResult = ref<any>(null)

// 版本历史相关
const versionDrawerVisible = ref(false)
const versionContentVisible = ref(false)
const versions = ref<any[]>([])
const selectedVersion = ref<any>(null)
const currentVersion = ref<number>(0)

// 执行历史相关
const executionHistoryDrawerVisible = ref(false)
const executionHistoryList = ref<any[]>([])
const autoShowRendered = ref(false)

// 智能分析相关
const analyzing = ref(false)
const quickAnalysis = ref<QuickAnalysisResult | null>(null)
const analysisResult = ref<PromptAnalysisResult | null>(null)

const commonTags = ['对话', '翻译', '写作', '代码', '分析', '创意', '教育', '商业']

const isEditMode = computed(() => !!route.params.id)
const variables = computed(() => extractVariables(formData.content))

// 评论相关
const promptOwnerId = ref<number | null>(null)
const versionNumbers = computed(() => versions.value.map((v: any) => v.version))
const isOwner = computed(() => promptOwnerId.value === userStore.userInfo?.id)

// 团队共享相关
const canEdit = ref(true)
const teamShared = ref(false)
const teamInfo = ref<{ team_id: number; team_name: string; permission: string } | null>(null)

// 多模型测试相关
const multiModelDialogVisible = ref(false)
const selectedModels = ref<string[]>([])
const multiModelRunning = ref(false)
const multiModelResults = ref<any[]>([])

// 获取当前Prompt的缓存key
const getCacheKey = () => {
  if (isEditMode.value) {
    return `prompt_variables_${route.params.id}`
  }
  return 'prompt_variables_new'
}

// 从 LocalStorage 加载变量值
function loadVariableValuesFromCache() {
  try {
    const cacheKey = getCacheKey()
    const cached = localStorage.getItem(cacheKey)
    if (cached) {
      const cachedData = JSON.parse(cached)
            
      // 兼容旧格式（直接是变量值对象）
      let cachedTextVars = cachedData.textVariables || cachedData
      let cachedFileVars = cachedData.fileVariables || {}
      
      // 只恢复当前 Prompt 中实际存在的变量
      const currentVars = variables.value
      const restoredTextValues: Record<string, string> = {}
      const restoredFileValues: Record<string, number> = {}
      
      currentVars.forEach(varName => {
        if (cachedTextVars[varName]) {
          restoredTextValues[varName] = cachedTextVars[varName]
        }
        if (cachedFileVars[varName]) {
          restoredFileValues[varName] = cachedFileVars[varName]
        }
      })
      
      if (Object.keys(restoredTextValues).length > 0) {
        variableValues.value = { ...variableValues.value, ...restoredTextValues }
              }
      
      if (Object.keys(restoredFileValues).length > 0) {
        fileVariableValues.value = { ...fileVariableValues.value, ...restoredFileValues }
              }
    }
  } catch (error) {
    console.error('恢复变量值失败:', error)
  }
}

// 保存变量值到 LocalStorage（防抖）
let saveTimer: any = null
function saveVariableValuesToCache() {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    try {
      const cacheKey = getCacheKey()
      const cacheData = {
        textVariables: variableValues.value,
        fileVariables: fileVariableValues.value
      }
      localStorage.setItem(cacheKey, JSON.stringify(cacheData))
          } catch (error) {
      console.error('保存变量值失败:', error)
    }
  }, 500)
}

// 监听变量值变化，自动保存（带防抖）
watch(variableValues, () => {
  saveVariableValuesToCache()
}, { deep: true })

// 监听文件变量值变化，自动保存
watch(fileVariableValues, () => {
  saveVariableValuesToCache()
}, { deep: true })

// ==================== 自动保存草稿 ====================
// 按用户隔离草稿
const DRAFT_KEY = computed(() => `prompt_draft_${userStore.userInfo?.id || 'anonymous'}`)
const DRAFT_INTERVAL = 30000 // 30秒自动保存
const lastSavedAt = ref<string | null>(null)
const hasDraft = ref(false)
let autoSaveTimer: ReturnType<typeof setInterval> | null = null

// 获取草稿
function getDraft() {
  try {
    const draft = localStorage.getItem(DRAFT_KEY.value)
    if (draft) {
      return JSON.parse(draft)
    }
  } catch (e) {
    console.error('读取草稿失败:', e)
  }
  return null
}

// 保存草稿
function saveDraft() {
  // 只在新建模式下保存草稿
  if (isEditMode.value) return

  // 如果没有内容，不保存
  if (!formData.title && !formData.content) return

  try {
    const draft = {
      title: formData.title,
      content: formData.content,
      description: formData.description,
      tags: formData.tags,
      is_public: formData.is_public,
      savedAt: new Date().toISOString()
    }
    localStorage.setItem(DRAFT_KEY.value, JSON.stringify(draft))
    lastSavedAt.value = new Date().toLocaleTimeString('zh-CN')
  } catch (e) {
    console.error('保存草稿失败:', e)
  }
}

// 恢复草稿
function restoreDraft() {
  const draft = getDraft()
  if (draft) {
    formData.title = draft.title || ''
    formData.content = draft.content || ''
    formData.description = draft.description || ''
    formData.tags = draft.tags || []
    formData.is_public = draft.is_public || false
    ElMessage.success('已恢复草稿')
    hasDraft.value = false
  }
}

// 清除草稿
function clearDraft() {
  localStorage.removeItem(DRAFT_KEY)
  hasDraft.value = false
}

// 启动自动保存
function startAutoSave() {
  if (autoSaveTimer) return
  autoSaveTimer = setInterval(saveDraft, DRAFT_INTERVAL)
}

// 停止自动保存
function stopAutoSave() {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
    autoSaveTimer = null
  }
}

// 监听表单变化，启动自动保存
watch(() => [formData.title, formData.content], () => {
  if (!isEditMode.value && (formData.title || formData.content)) {
    startAutoSave()
  }
}, { deep: true })

onMounted(async () => {
  // 添加键盘快捷键监听
  window.addEventListener('keydown', handleKeyDown)
  
  try {
    await configStore.loadAvailableModels()
      } catch (error) {
    console.error('❌ loadAvailableModels 失败:', error)
  }
  
  if (isEditMode.value) {
    await loadPrompt()
    
    // 加载完Prompt后，恢复变量缓存
    setTimeout(() => {
      loadVariableValuesFromCache()
    }, 100)
    
    // 检查是否需要自动打开版本历史
    if (route.query.showVersions === 'true') {
      await showVersionHistory()
    }
  } else {
    // 新建模式：检查是否有草稿
    const draft = getDraft()
    if (draft && (draft.title || draft.content)) {
      hasDraft.value = true
      // 提示用户是否恢复草稿
      ElMessageBox.confirm(
        `发现上次未保存的草稿（保存于 ${new Date(draft.savedAt).toLocaleString('zh-CN')}），是否恢复？`,
        '发现草稿',
        {
          confirmButtonText: '恢复草稿',
          cancelButtonText: '忽略',
          type: 'info'
        }
      ).then(() => {
        restoreDraft()
      }).catch(() => {
        clearDraft()
      })
    }
  }
})

// 组件卸载时停止自动保存
// 键盘快捷键处理
function handleKeyDown(e: KeyboardEvent) {
  // Ctrl+S 保存
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    if (canEdit.value && !saving.value) {
      handleSave()
    }
  }
  // Ctrl+Enter 运行
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault()
    if (!running.value) {
      handleRun()
    }
  }
}

onUnmounted(() => {
  stopAutoSave()
  // 移除键盘事件监听
  window.removeEventListener('keydown', handleKeyDown)
  // 页面离开前保存一次草稿
  if (!isEditMode.value) {
    saveDraft()
  }
})

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
    
    // 设置权限信息
    canEdit.value = prompt.can_edit !== false
    teamShared.value = prompt.team_shared || false
    teamInfo.value = prompt.team_info || null
  } catch (error) {
    ElMessage.error('加载失败')
    router.push('/prompts')
  }
}

function handleContentChange() {
  // 内容变化时自动提取变量
}

async function handleSave() {
  if (!formData.title || !formData.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }

  saving.value = true
  try {
    if (isEditMode.value) {
      await promptStore.updatePrompt(Number(route.params.id), formData)
    } else {
      const newPrompt = await promptStore.createPrompt(formData)
      // 保存成功后清除草稿
      clearDraft()
      stopAutoSave()
      router.replace(`/editor/${newPrompt.id}`)
    }
  } catch (error) {
    // 错误已处理
  } finally {
    saving.value = false
  }
}

async function handleRun() {
  if (!formData.content) {
    ElMessage.warning('请输入 Prompt 内容')
    return
  }

  running.value = true
  executionResult.value = null
  autoShowRendered.value = false // 正常运行不自动弹框
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

        // axios 拦截器返回的是 { data: ..., message: ... }
    executionResult.value = response.data
        
    // 执行成功后刷新历史记录列表
    if (isEditMode.value) {
      await loadExecutionHistory()
    }
  } catch (error) {
    console.error('❌ 执行失败:', error)
    ElMessage.error('执行失败')
  } finally {
    running.value = false
  }
}

function goBack() {
  router.push('/prompts')
}

// 删除 Prompt
async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个 Prompt 吗？此操作不可恢复，所有版本历史也会被删除。',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await promptStore.deletePrompt(Number(route.params.id))
    ElMessage.success('删除成功')
    router.push('/prompts')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      // 错误已在 store 中处理
    }
  }
}

// 多模型测试相关函数
function showMultiModelDialog() {
  if (!formData.content) {
    ElMessage.warning('请先输入 Prompt 内容')
    return
  }
  multiModelDialogVisible.value = true
  selectedModels.value = []
  multiModelResults.value = []
}

function toggleModel(modelId: string) {
  const index = selectedModels.value.indexOf(modelId)
  if (index > -1) {
    selectedModels.value.splice(index, 1)
  } else {
    selectedModels.value.push(modelId)
  }
}

async function runMultiModelTest() {
  if (selectedModels.value.length < 2) {
    ElMessage.warning('请至少选择 2 个模型进行对比')
    return
  }
  
  multiModelRunning.value = true
  multiModelResults.value = []
  
  try {
    // 并行执行多个模型
    const promises = selectedModels.value.map(async (modelId) => {
      const startTime = Date.now()
      try {
        const response = await runAPI.execute({
          prompt_id: isEditMode.value ? Number(route.params.id) : undefined,
          prompt_content: formData.content,
          variables: variableValues.value,
          file_variables: fileVariableValues.value,
          model: modelId,
          temperature: configStore.temperature,
          max_tokens: configStore.maxTokens
        })
        return {
          model: modelId,
          success: true,
          data: response.data,
          time: (Date.now() - startTime) / 1000
        }
      } catch (error: any) {
        return {
          model: modelId,
          success: false,
          error: error.message || '执行失败',
          time: (Date.now() - startTime) / 1000
        }
      }
    })
    
    multiModelResults.value = await Promise.all(promises)
    ElMessage.success('多模型测试完成')
  } catch (error) {
    ElMessage.error('测试失败')
  } finally {
    multiModelRunning.value = false
  }
}

// 版本历史相关函数
async function showVersionHistory() {
  if (!isEditMode.value) {
    ElMessage.warning('请先保存 Prompt')
    return
  }
  
  versionDrawerVisible.value = true
  await loadVersionHistory()
}

async function loadVersionHistory() {
  try {
    const response = await promptAPI.getVersions(Number(route.params.id)) as any
    versions.value = response.data.sort((a: any, b: any) => b.version - a.version)
    
    // 获取当前版本号（最大版本号）
    if (versions.value.length > 0) {
      currentVersion.value = Math.max(...versions.value.map((v: any) => v.version))
    }
    
      } catch (error) {
    console.error('加载版本历史失败:', error)
    ElMessage.error('加载版本历史失败')
  }
}

function viewVersionContent(version: any) {
  selectedVersion.value = version
  versionContentVisible.value = true
}

async function restoreVersion(version: any) {
  if (!version) return
  
  try {
    await ElMessageBox.confirm(
      `确定要恢复到版本 ${version.version} 吗？当前未保存的修改将会丢失。`,
      '恢复版本',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 恢复表单数据
    formData.title = version.title
    formData.content = version.content
    formData.description = version.description || ''
    formData.tags = version.tags || []
    
    // 自动保存
    await handleSave()
    
    ElMessage.success('已恢复到该版本')
    versionContentVisible.value = false
    versionDrawerVisible.value = false
    
    // 重新加载版本历史
    await loadVersionHistory()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复版本失败:', error)
      ElMessage.error('恢复版本失败')
    }
  }
}

// 执行历史相关函数
async function showExecutionHistory() {
  if (!isEditMode.value) {
    ElMessage.warning('请先保存 Prompt')
    return
  }
  
  executionHistoryDrawerVisible.value = true
  await loadExecutionHistory()
}

async function loadExecutionHistory() {
  try {
    const response = await executionHistoryAPI.getList({
      prompt_id: Number(route.params.id),
      skip: 0,
      limit: 50
    }) as any
    executionHistoryList.value = response.data.items || []
      } catch (error) {
    console.error('加载执行历史失败:', error)
    ElMessage.error('加载执行历史失败')
  }
}

function viewExecutionHistory(history: any) {
  // 将历史结果显示到结果查看器
  executionResult.value = {
    prompt_title: formData.title,
    prompt_content: history.prompt_content,
    final_prompt: history.final_prompt,
    variables: history.variables,
    output: history.output,
    model: history.model,
    input_tokens: history.input_tokens,
    output_tokens: history.output_tokens,
    total_tokens: history.total_tokens,
    cost: history.cost,
    response_time: history.response_time,
    is_cached: true,
    cached_at: history.created_at
  }
  
  // 设置自动显示渲染视图
  autoShowRendered.value = true
  
  // 切换到结果标签页
  activeTab.value = 'result'
  
  // 关闭抽屉
  executionHistoryDrawerVisible.value = false
  
  ElMessage.success('已加载历史执行结果')
}

function formatDate(dateString: string) {
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
    return `${minutes} 分钟前`
  }
  
  // 小于24小时
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    return `${hours} 小时前`
  }
  
  // 小于7天
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000))
    return `${days} 天前`
  }
  
  // 格式化为标准日期时间
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// ==================== 智能分析相关函数 ====================

// 获取分数颜色
function getScoreColor(score: number): string {
  if (score >= 80) return '#67c23a'  // 绿色
  if (score >= 60) return '#e6a23c'  // 橙色
  return '#f56c6c'  // 红色
}

// 获取维度名称
function getDimensionName(key: string): string {
  const names: Record<string, string> = {
    clarity: '清晰度',
    structure: '结构性',
    completeness: '完整性',
    executability: '可执行性'
  }
  return names[key] || key
}

// 快速分析（本地）
async function handleQuickAnalyze() {
  if (!formData.content) {
    ElMessage.warning('请先输入 Prompt 内容')
    return
  }
  
  try {
    const response = await promptAnalysisAPI.quickAnalyze({
      content: formData.content
    }) as any
    
    
    // 响应格式: { data: { success: true, analysis: {...} }, message: 'success' }
    if (response.data?.success && response.data?.analysis) {
      quickAnalysis.value = response.data.analysis
      ElMessage.success('快速分析完成')
    } else {
      ElMessage.warning('分析结果为空')
    }
  } catch (error) {
    console.error('快速分析失败:', error)
    ElMessage.error('快速分析失败')
  }
}

// AI 深度分析
async function handleAnalyze() {
  if (!formData.content) {
    ElMessage.warning('请先输入 Prompt 内容')
    return
  }
  
  analyzing.value = true
  analysisResult.value = null
  
  try {
    const response = await promptAnalysisAPI.analyze({
      content: formData.content,
      title: formData.title || undefined
    }) as any
    
    if (response.data?.success) {
      analysisResult.value = response.data.analysis
      ElMessage.success('AI 分析完成')
    } else {
      ElMessage.error(response.data?.error || '分析失败')
    }
  } catch (error: any) {
    console.error('AI 分析失败:', error)
    ElMessage.error(error.message || 'AI 分析失败，请检查 AI 配置')
  } finally {
    analyzing.value = false
  }
}

// 应用优化后的 Prompt
function applyOptimizedPrompt() {
  if (!analysisResult.value?.optimized_prompt) return
  
  ElMessageBox.confirm(
    '确定要应用优化后的 Prompt 吗？当前内容将被替换。',
    '应用优化',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    formData.content = analysisResult.value!.optimized_prompt
    ElMessage.success('已应用优化后的 Prompt')
  }).catch(() => {
    // 用户取消
  })
}

// 下载分析报告
function downloadReport() {
  if (!analysisResult.value) return
  
  const report = analysisResult.value
  const now = new Date().toLocaleString('zh-CN')
  
  // 构建 Markdown 格式报告
  let content = `# Prompt 分析报告

**生成时间**: ${now}
**Prompt 标题**: ${formData.title || '未命名'}

---

## 总体评分: ${report.overall_score}/100

### 维度评分

`
  
  // 添加维度评分
  if (report.dimensions) {
    for (const [key, dim] of Object.entries(report.dimensions)) {
      const dimInfo = dim as { score: number; comment: string }
      content += `#### ${getDimensionName(key)}: ${dimInfo.score}/100
${dimInfo.comment}

`
    }
  }
  
  // 添加优点
  if (report.strengths?.length) {
    content += `### 优点
${report.strengths.map(s => `- ${s}`).join('\n')}

`
  }
  
  // 添加待改进
  if (report.weaknesses?.length) {
    content += `### 待改进
${report.weaknesses.map(w => `- ${w}`).join('\n')}

`
  }
  
  // 添加改进建议
  if (report.suggestions?.length) {
    content += `### 改进建议
${report.suggestions.map((s, i) => `${i + 1}. **${s.title}** (${s.priority})
   ${s.description}`).join('\n\n')}

`
  }
  
  // 添加优化后的 Prompt
  if (report.optimized_prompt) {
    content += `### 优化后的 Prompt
\`\`\`
${report.optimized_prompt}
\`\`\`
`
  }
  
  // 下载文件
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `prompt-analysis-${formData.title || 'report'}-${new Date().toISOString().split('T')[0]}.md`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  ElMessage.success('报告下载成功')
}
</script>

<style scoped>
.prompt-editor-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.editor-container {
  flex: 1;
  overflow: hidden;
  padding: 1.5rem;
}

.editor-main {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  border: 1px solid #e1e4e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.toolbar {
  background: white;
  border-bottom: 1px solid #e1e4e8;
  padding: 1rem 1.5rem;
}

.toolbar .flex {
  align-items: center;
}

.toolbar .text-gray-400 {
  color: #cbd5e0;
  margin: 0 0.75rem;
}

.toolbar .text-gray-600 {
  color: #586069;
  font-weight: 600;
  font-size: 0.95rem;
}

.editor-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.editor-left {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 2.5rem;
  background: white;
}

.editor-left::-webkit-scrollbar {
  width: 8px;
}

.editor-left::-webkit-scrollbar-track {
  background: #f6f8fa;
}

.editor-left::-webkit-scrollbar-thumb {
  background: #d1d5da;
  border-radius: 4px;
}

.editor-left::-webkit-scrollbar-thumb:hover {
  background: #959da5;
}

.editor-right {
  width: 480px;
  background: #fafbfc;
  border-left: 1px solid #e1e4e8;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.editor-right :deep(.el-tabs) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-right :deep(.el-tabs__header) {
  margin: 0;
  background: white;
  padding: 1rem 1.5rem 0;
  border-bottom: 1px solid #e1e4e8;
}

.editor-right :deep(.el-tabs__item) {
  font-weight: 500;
  font-size: 0.9rem;
  color: #586069;
}

.editor-right :deep(.el-tabs__item:hover) {
  color: #0366d6;
}

.editor-right :deep(.el-tabs__item.is-active) {
  color: #24292e;
  font-weight: 600;
}

.editor-right :deep(.el-tabs__active-bar) {
  height: 2px;
  background: #0366d6;
}

.editor-right :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.editor-right :deep(.el-tabs__content)::-webkit-scrollbar {
  width: 8px;
}

.editor-right :deep(.el-tabs__content)::-webkit-scrollbar-track {
  background: #f6f8fa;
}

.editor-right :deep(.el-tabs__content)::-webkit-scrollbar-thumb {
  background: #d1d5da;
  border-radius: 4px;
}

.form-section {
  max-width: 900px;
  margin: 0;
}

.form-section :deep(.el-form-item__label) {
  font-weight: 600;
  color: #24292e;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.form-section :deep(.el-input__wrapper) {
  box-shadow: none !important;
  border-radius: 8px;
  transition: all 0.2s ease;
  background-color: #fafbfc;
  border: 1px solid #e1e4e8 !important;
  padding: 8px 12px;
}

.form-section :deep(.el-input__wrapper:hover) {
  border-color: #c8d1da !important;
  background-color: #ffffff;
}

.form-section :deep(.el-input__wrapper.is-focus) {
  border-color: #409eff !important;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1) !important;
}

.form-section :deep(.el-input__inner) {
  color: #24292e;
  font-size: 14px;
}

.form-section :deep(.el-textarea) {
  --el-input-border-color: transparent;
}

.form-section :deep(.el-textarea__inner) {
  box-shadow: none !important;
  border-radius: 8px;
  font-family: 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
  line-height: 1.7;
  transition: all 0.2s ease;
  background-color: #fafbfc;
  color: #24292e;
  font-size: 14px;
  border: 1px solid #e1e4e8 !important;
  padding: 12px 14px;
  resize: vertical;
}

.form-section :deep(.el-textarea__inner:hover) {
  border-color: #c8d1da !important;
  background-color: #ffffff;
}

.form-section :deep(.el-textarea__inner:focus) {
  border-color: #409eff !important;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1) !important;
  outline: none;
}

.form-section :deep(.el-textarea__inner::placeholder),
.form-section :deep(.el-input__inner::placeholder) {
  color: #94a3b8;
  font-weight: 400;
}

.form-section :deep(.el-select) {
  width: 100%;
}

.form-section :deep(.el-form-item__content) {
  width: 100%;
}

.form-section :deep(.el-checkbox) {
  font-size: 0.95rem;
  color: #4a5568;
}

.settings-panel {
  padding: 0;
}

.settings-panel :deep(.el-form-item__label) {
  font-weight: 600;
  color: #2d3748;
}

.text-xs {
  font-size: 0.75rem;
  line-height: 1rem;
}

.text-gray-500 {
  color: #6b7280;
}

.mt-1 {
  margin-top: 0.25rem;
}

/* 按钮优化 */
:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.15s;
}

:deep(.el-button--primary) {
  background: #0366d6;
  border-color: #0366d6;
}

:deep(.el-button--primary:hover) {
  background: #0256c5;
  border-color: #0256c5;
}

:deep(.el-button--success) {
  background: #28a745;
  border-color: #28a745;
}

:deep(.el-button--success:hover) {
  background: #22863a;
  border-color: #22863a;
}

:deep(.el-button--danger) {
  background: #d73a49;
  border-color: #d73a49;
}

:deep(.el-button--danger:hover) {
  background: #cb2431;
  border-color: #cb2431;
}

/* 版本历史样式 */
.version-history-container {
  padding: 1rem;
  background: #fafbfc;
}

.version-card {
  margin-bottom: 1rem;
  border-radius: 6px;
  transition: all 0.15s;
  border: 1px solid #e1e4e8;
  background: white;
}

.version-card:hover {
  box-shadow: 0 1px 5px rgba(27, 31, 35, 0.1);
  border-color: #d1d5da;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e1e4e8;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.version-number {
  font-weight: 600;
  font-size: 1rem;
  color: #0366d6;
}

.version-actions {
  display: flex;
  gap: 0.5rem;
}

.version-summary {
  padding: 0.5rem 0;
}

.version-title {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.version-change {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: #f1f5f9;
  border-radius: 4px;
  border-left: 3px solid #3b82f6;
}

.version-meta {
  color: #94a3b8;
  font-size: 0.85rem;
}

.version-content-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.version-meta-info {
  margin-bottom: 1.5rem;
}

.version-content-preview {
  margin-top: 1.5rem;
}

.version-content-preview h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.content-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.content-box pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #334155;
}

:deep(.el-timeline) {
  padding-left: 0;
}

:deep(.el-timeline-item__timestamp) {
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 500;
}

:deep(.el-drawer__header) {
  margin-bottom: 1.5rem;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 2px solid #e2e8f0;
}

:deep(.el-drawer__title) {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

:deep(.el-drawer__body) {
  padding: 0;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #475569;
}

:deep(.el-descriptions__content) {
  color: #1e293b;
}

/* 执行历史样式 */
.execution-history-container {
  padding: 1rem;
  background: #fafbfc;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-card {
  border-radius: 6px;
  transition: all 0.15s;
  border: 1px solid #e1e4e8;
  background: white;
}

.history-card:hover {
  box-shadow: 0 1px 5px rgba(27, 31, 35, 0.1);
  border-color: #d1d5da;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e1e4e8;
}

.history-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #586069;
  font-size: 0.85rem;
  font-weight: 500;
}

.history-time .el-icon {
  font-size: 1rem;
  color: #0366d6;
}

.history-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.info-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.info-row .label {
  color: #586069;
  font-weight: 500;
}

.info-row .value {
  color: #24292e;
  font-weight: 600;
}

/* ==================== 智能分析面板样式 ==================== */
.analysis-panel {
  padding: 1rem;
  height: 100%;
  overflow-y: auto;
}

.analysis-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

/* 快速分析结果 */
.quick-analysis {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.quick-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.score-label {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #64748b;
}

.quick-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
}

.stat-value {
  font-weight: 600;
  color: #1e293b;
}

.quick-tips {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
}

.tip-warning {
  background: #fef3c7;
  color: #92400e;
}

.tip-suggestion {
  background: #e0f2fe;
  color: #0369a1;
}

.tip-info {
  background: #f0fdf4;
  color: #166534;
}

/* AI 分析结果 */
.ai-analysis {
  background: white;
  border-radius: 8px;
}

.analysis-header {
  position: relative;
}

.analysis-header .download-btn {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
}

.overall-score {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.score-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
}

.score-text {
  font-size: 0.85rem;
  color: #64748b;
  display: block;
}

/* 维度评分 */
.dimensions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.dimension-item {
  background: #f8fafc;
  border-radius: 8px;
  padding: 0.75rem;
}

.dim-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.dim-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.9rem;
}

.dim-score {
  font-weight: 700;
  color: #3b82f6;
}

.dim-comment {
  font-size: 0.8rem;
  color: #64748b;
  margin-top: 0.5rem;
}

/* 优缺点 */
.strengths-weaknesses {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.sw-section {
  padding: 1rem;
  border-radius: 8px;
}

.sw-section h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
}

.sw-section ul {
  margin: 0;
  padding-left: 1.25rem;
}

.sw-section li {
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.strengths {
  background: #f0fdf4;
}

.strengths h4 {
  color: #166534;
}

.strengths li {
  color: #166534;
}

.weaknesses {
  background: #fff7ed;
}

.weaknesses h4 {
  color: #c2410c;
}

.weaknesses li {
  color: #c2410c;
}

/* 改进建议 */
.suggestions {
  margin-bottom: 1.5rem;
}

.suggestions h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #1e293b;
}

.sug-title {
  margin-left: 0.5rem;
  font-weight: 500;
}

.sug-content {
  padding: 0.5rem 0;
}

.sug-content p {
  margin: 0 0 0.75rem 0;
  color: #475569;
  line-height: 1.6;
}

.sug-example {
  background: #f8fafc;
  border-radius: 6px;
  padding: 0.75rem;
}

.sug-example pre {
  margin: 0.5rem 0 0 0;
  white-space: pre-wrap;
  font-size: 0.85rem;
  color: #1e293b;
}

/* 最佳实践检查 */
.best-practices {
  margin-bottom: 1.5rem;
}

.best-practices h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #1e293b;
}

.practice-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.practice-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
}

.practice-item.pass {
  background: #f0fdf4;
  color: #166534;
}

.practice-item.fail {
  background: #fef2f2;
  color: #b91c1c;
}

.practice-rule {
  font-weight: 600;
}

.practice-msg {
  color: inherit;
  opacity: 0.85;
}

/* 优化后的 Prompt */
.optimized-prompt h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #1e293b;
}

.optimized-content {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
}

.optimized-content pre {
  margin: 0 0 1rem 0;
  white-space: pre-wrap;
  font-size: 0.85rem;
  line-height: 1.6;
  color: #1e293b;
  max-height: 300px;
  overflow-y: auto;
}

/* 只读提示条 */
.readonly-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 1px solid #fbbf24;
  border-radius: 8px;
  margin-bottom: 1rem;
  color: #92400e;
  font-size: 0.875rem;
}

.readonly-banner .el-icon {
  font-size: 1.1rem;
  color: #d97706;
}

.readonly-banner strong {
  color: #78350f;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .editor-container {
    padding: 1rem !important;
  }
  
  .toolbar {
    padding: 0.75rem 1rem !important;
  }
  
  .toolbar .flex {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .toolbar .flex > div {
    width: 100%;
    justify-content: space-between;
  }
  
  .toolbar .space-x-2 {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .toolbar .space-x-2 .el-button {
    flex: 1;
    min-width: 0;
  }
  
  .editor-content {
    flex-direction: column !important;
    gap: 1rem;
  }
  
  .editor-left,
  .editor-right {
    width: 100% !important;
    min-width: 0 !important;
  }
  
  .editor-right {
    height: auto !important;
    max-height: 50vh;
  }
  
  .form-section {
    padding: 1rem !important;
  }
  
  .dimensions {
    grid-template-columns: 1fr;
  }
  
  .strengths-weaknesses {
    grid-template-columns: 1fr;
  }
  
  .readonly-banner {
    font-size: 0.8rem;
    padding: 0.5rem 0.75rem;
  }
}

@media (max-width: 480px) {
  .toolbar .space-x-2 .el-button span {
    display: none;
  }
  
  .toolbar .space-x-2 .el-button {
    padding: 8px 12px;
  }
}

/* 多模型测试对话框样式 */
.multi-model-dialog .model-selection {
  margin-bottom: 20px;
}

.multi-model-dialog .selection-header {
  margin-bottom: 16px;
}

.multi-model-dialog .selection-header .title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.multi-model-dialog .selection-header .subtitle {
  font-size: 13px;
  color: #909399;
  margin-left: 8px;
}

.multi-model-dialog .model-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.multi-model-dialog .model-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fafbfc;
}

.multi-model-dialog .model-card:hover {
  border-color: #c0c4cc;
  background: #fff;
}

.multi-model-dialog .model-card.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.multi-model-dialog .model-info {
  flex: 1;
}

.multi-model-dialog .model-info .model-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.multi-model-dialog .model-info .model-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.multi-model-dialog .selection-status {
  margin-top: 12px;
  font-size: 13px;
  color: #606266;
}

/* 对比统计表 */
.multi-model-dialog .compare-stats-table {
  margin-bottom: 20px;
}

.multi-model-dialog .compare-stats-table :deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

.multi-model-dialog .model-cell {
  font-weight: 500;
}

/* 输出对比 */
.multi-model-dialog .compare-outputs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 16px;
  max-height: 500px;
  overflow-y: auto;
}

.multi-model-dialog .output-panel {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}

.multi-model-dialog .output-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border-bottom: 1px solid #ebeef5;
}

.multi-model-dialog .output-model {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.multi-model-dialog .output-content {
  padding: 0;
  max-height: 350px;
  overflow-y: auto;
}

.multi-model-dialog .output-content :deep(.result-viewer) {
  border: none;
  border-radius: 0;
}

.multi-model-dialog .output-error {
  padding: 20px;
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
</style>

