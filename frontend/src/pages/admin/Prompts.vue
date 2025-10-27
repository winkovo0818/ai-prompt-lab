<template>
  <div class="admin-prompts-page">
    <Header />
    
    <div class="content">
      <el-card>
        <template #header>
          <h2>Prompt 管理</h2>
        </template>

        <div class="search-bar">
          <el-input v-model="searchText" placeholder="搜索 Prompt 标题或描述" clearable @clear="loadPrompts" style="width: 300px">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="loadPrompts">搜索</el-button>
        </div>

        <el-table :data="prompts" style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="username" label="创建者" width="120" />
          <el-table-column prop="is_public" label="公开" width="100">
            <template #default="scope">
              <el-switch 
                v-model="scope.row.is_public" 
                @change="togglePublic(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button size="small" type="danger" @click="deletePrompt(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadPrompts"
          @size-change="loadPrompts"
          style="margin-top: 20px; justify-content: flex-end"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import Header from '@/components/Layout/Header.vue'

const loading = ref(false)
const prompts = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')

onMounted(() => {
  loadPrompts()
})

async function loadPrompts() {
  loading.value = true
  try {
    const response = await adminAPI.getAllPrompts({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchText.value || undefined
    }) as any

    prompts.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('加载 Prompt 列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleString('zh-CN')
}

async function togglePublic(prompt: any) {
  try {
    await adminAPI.togglePromptPublic(prompt.id, prompt.is_public)
    ElMessage.success(`Prompt 已${prompt.is_public ? '公开' : '设为私有'}`)
  } catch (error: any) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
    prompt.is_public = !prompt.is_public
  }
}

async function deletePrompt(prompt: any) {
  try {
    await ElMessageBox.confirm(`确定要删除 Prompt "${prompt.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await adminAPI.deletePrompt(prompt.id)
    ElMessage.success('Prompt 删除成功')
    await loadPrompts()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.admin-prompts-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.content {
  flex: 1;
  padding: 2rem;
}

.search-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
</style>

