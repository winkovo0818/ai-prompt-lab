<template>
  <div class="sensitive-words-table">
    <el-table 
      :data="words" 
      v-loading="loading"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="word" label="敏感词" width="200" />
      <el-table-column label="分类" width="120">
        <template #default="{ row }">
          <el-tag :type="getCategoryType(row.category)" size="small">
            {{ getCategoryText(row.category) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="严重程度" width="150">
        <template #default="{ row }">
          <el-progress 
            :percentage="row.severity" 
            :color="getSeverityColor(row.severity)"
            :stroke-width="12"
          />
        </template>
      </el-table-column>
      <el-table-column label="来源" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_system" type="info" size="small">系统</el-tag>
          <el-tag v-else type="success" size="small">自定义</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_active" type="success" size="small">启用</el-tag>
          <el-tag v-else type="info" size="small">禁用</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button
            v-if="!row.is_system"
            type="danger"
            size="small"
            link
            @click="deleteWord(row)"
          >
            删除
          </el-button>
          <el-tooltip v-else content="系统内置词不可删除">
            <el-button size="small" link disabled>删除</el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'

const props = defineProps<{
  category?: string | null
}>()

const emit = defineEmits(['refresh'])

const loading = ref(false)
const words = ref<any[]>([])

watch(() => props.category, () => {
  loadWords()
}, { immediate: true })

onMounted(() => {
  loadWords()
})

async function loadWords() {
  loading.value = true
  try {
    const params: any = {}
    if (props.category) {
      params.category = props.category
    }
    
    const response = await request.get('/api/security/sensitive-words', { params })
    words.value = response.data.items || []
  } catch (error: any) {
    console.error('加载敏感词失败:', error)
  } finally {
    loading.value = false
  }
}

async function deleteWord(word: any) {
  try {
    await ElMessageBox.confirm(
      `确定要删除敏感词"${word.word}"吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await request.delete(`/api/security/sensitive-words/${word.id}`)
    ElMessage.success('删除成功')
    loadWords()
    emit('refresh')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

function getCategoryType(category: string) {
  const types: Record<string, any> = {
    nsfw: 'danger',
    illegal: 'danger',
    fraud: 'warning',
    custom: 'primary'
  }
  return types[category] || 'info'
}

function getCategoryText(category: string) {
  const texts: Record<string, string> = {
    nsfw: '暴力色情',
    illegal: '违法内容',
    fraud: '欺诈诈骗',
    custom: '自定义',
    political: '政治敏感',
    discrimination: '歧视内容'
  }
  return texts[category] || category
}

function getSeverityColor(severity: number) {
  if (severity >= 80) return '#f56c6c'
  if (severity >= 50) return '#e6a23c'
  return '#67c23a'
}

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

defineExpose({
  loadWords
})
</script>

<style scoped>
.sensitive-words-table {
  min-height: 200px;
}
</style>

