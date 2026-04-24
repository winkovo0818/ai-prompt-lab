<template>
  <el-dialog v-model="visible" title="版本对比" width="800px">
    <!-- Diff 头部信息 -->
    <div class="diff-header">
      <div class="diff-from">
        <el-tag type="info">From</el-tag>
        <span class="version-title">{{ fromCommit?.title }}</span>
      </div>
      <div class="diff-arrow">→</div>
      <div class="diff-to">
        <el-tag type="success">To</el-tag>
        <span class="version-title">{{ toCommit?.title }}</span>
      </div>
    </div>

    <!-- 统计 -->
    <div class="diff-stats">
      <span class="additions">+{{ diffResult?.additions || 0 }} 行</span>
      <span class="deletions">-{{ diffResult?.deletions || 0 }} 行</span>
    </div>

    <!-- Diff 内容 -->
    <div class="diff-content" v-loading="loading">
      <div
        v-for="(segment, idx) in diffResult?.segments"
        :key="idx"
        :class="['diff-segment', segment.type]"
      >
        <div
          v-for="(line, lineIdx) in segment.lines"
          :key="lineIdx"
          class="diff-line"
        >
          <span class="line-prefix">{{ getLinePrefix(segment.type) }}</span>
          <span class="line-content">{{ line }}</span>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { getDiff } from '@/api/git'

const props = defineProps<{
  modelValue: boolean
  promptId: number
  fromCommitId?: number
  toCommitId?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const visible = ref(false)
const loading = ref(false)
const fromCommit = ref<any>(null)
const toCommit = ref<any>(null)
const diffResult = ref<any>(null)

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.fromCommitId && props.toCommitId) {
    loadDiff()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const loadDiff = async () => {
  loading.value = true
  try {
    const res = await getDiff(props.promptId, props.fromCommitId!, props.toCommitId!)
    fromCommit.value = res.data?.from
    toCommit.value = res.data?.to
    diffResult.value = res.data?.diff
  } catch (err) {
    console.error('加载差异失败', err)
  } finally {
    loading.value = false
  }
}

const getLinePrefix = (type: string) => {
  switch (type) {
    case 'added': return '+'
    case 'deleted': return '-'
    default: return ' '
  }
}
</script>

<style scoped>
.diff-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}
.diff-from, .diff-to {
  display: flex;
  align-items: center;
  gap: 8px;
}
.version-title {
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.diff-arrow {
  color: #409eff;
  font-size: 18px;
}
.diff-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}
.additions {
  color: #22863a;
  font-weight: 500;
}
.deletions {
  color: #cb2431;
  font-weight: 500;
}
.diff-content {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  max-height: 400px;
  overflow: auto;
  font-family: 'Consolas', monospace;
  font-size: 13px;
}
.diff-segment.unchanged {
  color: #666;
  background: #fff;
}
.diff-segment.added {
  background: #e6ffec;
}
.diff-segment.deleted {
  background: #ffeef0;
}
.diff-line {
  display: flex;
  padding: 2px 8px;
  line-height: 1.5;
}
.line-prefix {
  width: 20px;
  flex-shrink: 0;
  color: #999;
}
.diff-segment.added .line-prefix {
  color: #22863a;
}
.diff-segment.deleted .line-prefix {
  color: #cb2431;
}
.line-content {
  white-space: pre-wrap;
  word-break: break-all;
}
</style>