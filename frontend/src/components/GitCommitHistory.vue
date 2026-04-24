<template>
  <div class="commit-history">
    <div class="history-header">
      <h4>版本历史</h4>
      <el-button size="small" @click="loadCommits" :loading="loading">
        <el-icon><refresh /></el-icon>
      </el-button>
    </div>

    <div class="timeline" v-loading="loading">
      <div v-if="commits.length === 0" class="empty-state">
        暂无提交记录
      </div>

      <div
        v-for="(commit, index) in commits"
        :key="commit.id"
        class="timeline-item"
        :class="{ active: selectedCommit?.id === commit.id }"
        @click="handleSelectCommit(commit)"
      >
        <div class="timeline-marker">
          <div class="dot"></div>
          <div class="line" v-if="index < commits.length - 1"></div>
        </div>
        <div class="timeline-content">
          <div class="commit-title">{{ commit.title }}</div>
          <div class="commit-meta">
            <span class="commit-time">{{ formatTime(commit.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        small
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { getCommits } from '@/api/git'

const props = defineProps<{
  promptId: number
  branchId: number
}>()

const emit = defineEmits<{
  (e: 'select', commit: any): void
}>()

const commits = ref<any[]>([])
const selectedCommit = ref<any>(null)
const loading = ref(false)
const total = ref(0)
const pageSize = 20
const currentPage = ref(1)

const loadCommits = async () => {
  if (!props.branchId) return
  loading.value = true
  try {
    const res = await getCommits(props.promptId, props.branchId, currentPage.value, pageSize)
    commits.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (err) {
    console.error('加载提交历史失败', err)
  } finally {
    loading.value = false
  }
}

const handleSelectCommit = (commit: any) => {
  selectedCommit.value = commit
  emit('select', commit)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadCommits()
}

const formatTime = (time: string) => {
  const date = new Date(time)
  return date.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

watch(() => props.branchId, () => {
  currentPage.value = 1
  loadCommits()
})

onMounted(() => {
  loadCommits()
})
</script>

<style scoped>
.commit-history {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.history-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}
.timeline {
  max-height: 400px;
  overflow-y: auto;
}
.timeline-item {
  display: flex;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
}
.timeline-item:hover {
  background: #f5f7fa;
}
.timeline-item.active {
  background: #ecf5ff;
}
.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 16px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  flex-shrink: 0;
}
.line {
  width: 2px;
  flex: 1;
  background: #e4e7ed;
  min-height: 20px;
}
.timeline-content {
  margin-left: 12px;
  flex: 1;
}
.commit-title {
  font-size: 13px;
  color: #333;
  line-height: 1.4;
}
.commit-meta {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 0;
}
.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: center;
}
</style>