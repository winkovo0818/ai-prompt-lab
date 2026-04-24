<template>
  <div class="prompt-repo">
    <el-row :gutter="20">
      <!-- 左侧：分支和 PR 列表 -->
      <el-col :span="8">
        <GitBranchManager
          :prompt-id="promptId"
          v-model="currentBranchId"
          @branch-changed="handleBranchChanged"
        />

        <div class="section-gap"></div>

        <GitPRList
          :prompt-id="promptId"
          @select="handlePRSelect"
        />
      </el-col>

      <!-- 右侧：版本历史 -->
      <el-col :span="16">
        <div class="history-panel">
          <div class="panel-header">
            <h3>版本历史</h3>
            <el-button type="primary" size="small" @click="showCommitDialog = true">
              提交变更
            </el-button>
          </div>

          <GitCommitHistory
            v-if="currentBranchId"
            :key="currentBranchId"
            :prompt-id="promptId"
            :branch-id="currentBranchId"
            @select="handleCommitSelect"
          />

          <div v-if="!currentBranchId" class="empty-state">
            请先选择一个分支
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Diff 查看对话框 -->
    <GitDiffViewer
      v-model="showDiffDialog"
      :prompt-id="promptId"
      :from-commit-id="diffFromCommitId"
      :to-commit-id="diffToCommitId"
    />

    <!-- 提交对话框 -->
    <el-dialog v-model="showCommitDialog" title="提交变更" width="500px">
      <el-form :model="commitForm" label-width="80px">
        <el-form-item label="提交信息">
          <el-input v-model="commitForm.title" placeholder="描述本次变更" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="commitForm.content" type="textarea" :rows="6" placeholder="Prompt 内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCommitDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCommit">提交</el-button>
      </template>
    </el-dialog>

    <!-- PR 详情对话框 -->
    <el-dialog v-model="showPRDetailDialog" title="PR 详情" width="600px">
      <div v-if="selectedPR" class="pr-detail">
        <div class="pr-info">
          <h4>{{ selectedPR.title }}</h4>
          <p>{{ selectedPR.description }}</p>
        </div>
        <div class="pr-branches">
          <span class="branch-tag">{{ selectedPR.source_branch?.name }}</span>
          <span class="arrow">→</span>
          <span class="branch-tag">{{ selectedPR.target_branch?.name }}</span>
        </div>
        <div class="pr-actions">
          <el-button
            v-if="selectedPR.can_merge && selectedPR.status === 'open'"
            type="success"
            @click="handleMergePR"
          >
            合并 PR
          </el-button>
          <el-button
            v-if="selectedPR.status === 'open'"
            type="danger"
            @click="handleClosePR"
          >
            关闭 PR
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import GitBranchManager from '@/components/GitBranchManager.vue'
import GitCommitHistory from '@/components/GitCommitHistory.vue'
import GitPRList from '@/components/GitPRList.vue'
import GitDiffViewer from '@/components/GitDiffViewer.vue'
import { createCommit, revertCommit, mergePullRequest, closePullRequest, getPullRequest } from '@/api/git'

const props = defineProps<{
  promptId: number
}>()

const currentBranchId = ref<number | undefined>()
const showCommitDialog = ref(false)
const showDiffDialog = ref(false)
const showPRDetailDialog = ref(false)
const diffFromCommitId = ref<number>()
const diffToCommitId = ref<number>()
const selectedPR = ref<any>(null)

const commitForm = ref({
  title: '',
  content: ''
})

const handleBranchChanged = (data: any) => {
  if (data.content) {
    commitForm.value.content = data.content
  }
}

const handleCommitSelect = (commit: any) => {
  // 简单查看：直接显示内容
  // 实际可以显示更详细的 commit 信息
  console.log('选择提交', commit)
}

const handlePRSelect = async (pr: any) => {
  try {
    const res = await getPullRequest(props.promptId, pr.id)
    selectedPR.value = res.data
    showPRDetailDialog.value = true
  } catch (err) {
    console.error('加载 PR 详情失败', err)
  }
}

const handleCommit = async () => {
  if (!currentBranchId.value) {
    ElMessage.warning('请先选择分支')
    return
  }
  if (!commitForm.value.title) {
    ElMessage.warning('请输入提交信息')
    return
  }
  try {
    await createCommit(props.promptId, {
      branch_id: currentBranchId.value,
      title: commitForm.value.title,
      content: commitForm.value.content
    })
    ElMessage.success('提交成功')
    showCommitDialog.value = false
    commitForm.value = { title: '', content: '' }
  } catch (err) {
    console.error('提交失败', err)
  }
}

const handleMergePR = async () => {
  if (!selectedPR.value) return
  try {
    await mergePullRequest(props.promptId, selectedPR.value.id)
    ElMessage.success('PR 已合并')
    showPRDetailDialog.value = false
  } catch (err) {
    console.error('合并 PR 失败', err)
  }
}

const handleClosePR = async () => {
  if (!selectedPR.value) return
  try {
    await closePullRequest(props.promptId, selectedPR.value.id)
    ElMessage.success('PR 已关闭')
    showPRDetailDialog.value = false
  } catch (err) {
    console.error('关闭 PR 失败', err)
  }
}
</script>

<style scoped>
.prompt-repo {
  padding: 20px;
}
.section-gap {
  height: 20px;
}
.history-panel {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  min-height: 500px;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.panel-header h3 {
  margin: 0;
}
.empty-state {
  text-align: center;
  color: #999;
  padding: 60px 0;
}
.pr-detail {
  padding: 10px;
}
.pr-info h4 {
  margin: 0 0 10px 0;
}
.pr-branches {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 16px 0;
}
.branch-tag {
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
}
.arrow {
  color: #409eff;
}
.pr-actions {
  display: flex;
  gap: 8px;
}
</style>