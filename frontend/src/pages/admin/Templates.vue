<template>
  <div class="admin-templates-page">
    <Header />
    
    <div class="content">
      <el-card>
        <template #header>
          <div class="flex items-center justify-between">
            <h2>模板库管理</h2>
            <el-button type="primary" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              新建模板
            </el-button>
          </div>
        </template>

        <div class="search-bar">
          <el-input 
            v-model="searchText" 
            placeholder="搜索模板标题" 
            clearable 
            @clear="loadTemplates" 
            style="width: 300px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select 
            v-model="filterCategory" 
            placeholder="分类筛选" 
            clearable
            @change="loadTemplates"
            style="width: 200px; margin-left: 10px"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
          <el-button type="primary" @click="loadTemplates">搜索</el-button>
        </div>

        <el-table :data="templates" style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column prop="category_name" label="分类" width="120" />
          <el-table-column prop="difficulty" label="难度" width="100">
            <template #default="scope">
              <el-tag :type="getDifficultyType(scope.row.difficulty)" size="small">
                {{ getDifficultyText(scope.row.difficulty) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="use_count" label="使用次数" width="100" />
          <el-table-column prop="favorite_count" label="收藏" width="80" />
          <el-table-column label="状态" width="120">
            <template #default="scope">
              <el-switch 
                v-model="scope.row.is_featured" 
                active-text="精选"
                @change="toggleFeatured(scope.row)"
                style="margin-right: 10px"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadTemplates"
          @size-change="loadTemplates"
          style="margin-top: 20px; justify-content: flex-end"
        />
      </el-card>
    </div>

    <!-- 创建/编辑模板对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingTemplate ? '编辑模板' : '新建模板'"
      width="900px"
      destroy-on-close
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="模板标题" required>
          <el-input v-model="formData.title" placeholder="输入模板标题" />
        </el-form-item>

        <el-form-item label="所属分类" required>
          <el-select v-model="formData.category_id" placeholder="选择分类">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="描述">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="2"
            placeholder="简单描述这个模板的用途"
          />
        </el-form-item>

        <el-form-item label="Prompt 内容" required>
          <el-input 
            v-model="formData.content" 
            type="textarea" 
            :rows="10"
            placeholder="输入 Prompt 内容，使用 {{变量名}} 添加变量"
          />
        </el-form-item>

        <el-form-item label="变量定义">
          <div class="variables-editor">
            <div 
              v-for="(variable, index) in formData.variables" 
              :key="index"
              class="variable-item"
            >
              <el-input 
                v-model="variable.name" 
                placeholder="变量名" 
                style="width: 150px"
              />
              <el-input 
                v-model="variable.description" 
                placeholder="描述" 
                style="width: 200px; margin-left: 10px"
              />
              <el-input 
                v-model="variable.default_value" 
                placeholder="默认值" 
                style="width: 200px; margin-left: 10px"
              />
              <el-button 
                type="danger" 
                size="small" 
                @click="removeVariable(index)"
                style="margin-left: 10px"
              >
                删除
              </el-button>
            </div>
            <el-button @click="addVariable" style="margin-top: 10px">
              <el-icon><Plus /></el-icon>
              添加变量
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="标签">
          <el-select 
            v-model="formData.tags" 
            multiple 
            filterable 
            allow-create
            placeholder="添加标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in commonTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="难度">
          <el-radio-group v-model="formData.difficulty">
            <el-radio label="beginner">入门</el-radio>
            <el-radio label="intermediate">中级</el-radio>
            <el-radio label="advanced">高级</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="示例输入">
          <el-input 
            v-model="exampleInputStr" 
            type="textarea" 
            :rows="3"
            placeholder='JSON 格式，例如: {"变量名": "示例值"}'
          />
        </el-form-item>

        <el-form-item label="示例输出">
          <el-input 
            v-model="formData.example_output" 
            type="textarea" 
            :rows="3"
            placeholder="输入示例输出结果"
          />
        </el-form-item>

        <el-form-item label="精选模板">
          <el-switch v-model="formData.is_featured" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminAPI, templateAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import Header from '@/components/Layout/Header.vue'

const loading = ref(false)
const saving = ref(false)
const templates = ref<any[]>([])
const categories = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const filterCategory = ref<number | undefined>(undefined)

const dialogVisible = ref(false)
const editingTemplate = ref<any>(null)
const exampleInputStr = ref('')

const formData = ref({
  title: '',
  category_id: undefined as number | undefined,
  description: '',
  content: '',
  variables: [] as Array<{ name: string; description: string; default_value: string }>,
  tags: [] as string[],
  difficulty: 'beginner',
  example_output: '',
  is_featured: false
})

const commonTags = ['翻译', '写作', '编程', '分析', '创意', '教育', '商业', '对话']

onMounted(async () => {
  // 先加载分类，再加载模板
  await loadCategories()
  await loadTemplates()
})

async function loadCategories() {
  try {
    const response = await templateAPI.getCategories() as any
    categories.value = response.data
    console.log('✅ 分类加载成功:', categories.value)
  } catch (error) {
    console.error('❌ 加载分类失败:', error)
  }
}

async function loadTemplates() {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchText.value) {
      params.search = searchText.value
    }
    
    if (filterCategory.value) {
      params.category_id = filterCategory.value
    }

    const response = await templateAPI.getList(params) as any
    console.log('📦 模板数据:', response.data.items)
    
    templates.value = response.data.items.map((item: any) => {
      const category = categories.value.find(c => c.id === item.category_id)
      console.log(`模板 ${item.id} (category_id: ${item.category_id}) -> 分类: ${category?.name || '未找到'}`)
      return {
        ...item,
        category_name: category?.name || '未知'
      }
    })
    total.value = response.data.total
  } catch (error) {
    console.error('❌ 加载模板列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dateString: string) {
  if (!dateString) return '-'
  
  try {
    const date = new Date(dateString)
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      console.warn('无效的日期格式:', dateString)
      return '-'
    }
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('日期格式化错误:', error, dateString)
    return '-'
  }
}

function getDifficultyType(difficulty: string) {
  const map: Record<string, any> = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'danger'
  }
  return map[difficulty] || 'info'
}

function getDifficultyText(difficulty: string) {
  const map: Record<string, string> = {
    beginner: '入门',
    intermediate: '中级',
    advanced: '高级'
  }
  return map[difficulty] || '未知'
}

async function toggleFeatured(template: any) {
  try {
    await adminAPI.updateTemplate(template.id, {
      is_featured: template.is_featured
    })
    ElMessage.success('更新成功')
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败')
    template.is_featured = !template.is_featured
  }
}

function showCreateDialog() {
  editingTemplate.value = null
  formData.value = {
    title: '',
    category_id: undefined,
    description: '',
    content: '',
    variables: [],
    tags: [],
    difficulty: 'beginner',
    example_output: '',
    is_featured: false
  }
  exampleInputStr.value = ''
  dialogVisible.value = true
}

function handleEdit(template: any) {
  editingTemplate.value = template
  formData.value = {
    title: template.title,
    category_id: template.category_id,
    description: template.description || '',
    content: template.content,
    variables: template.variables || [],
    tags: template.tags || [],
    difficulty: template.difficulty,
    example_output: template.example_output || '',
    is_featured: template.is_featured
  }
  exampleInputStr.value = template.example_input ? JSON.stringify(template.example_input, null, 2) : ''
  dialogVisible.value = true
}

async function handleSave() {
  if (!formData.value.title || !formData.value.content || !formData.value.category_id) {
    ElMessage.warning('请填写必填项')
    return
  }

  saving.value = true
  try {
    const data: any = {
      title: formData.value.title,
      category_id: formData.value.category_id,
      description: formData.value.description,
      content: formData.value.content,
      variables: formData.value.variables,
      tags: formData.value.tags,
      difficulty: formData.value.difficulty,
      example_output: formData.value.example_output,
      is_featured: formData.value.is_featured
    }

    // 解析示例输入
    if (exampleInputStr.value) {
      try {
        data.example_input = JSON.parse(exampleInputStr.value)
      } catch (e) {
        ElMessage.warning('示例输入的 JSON 格式不正确')
        return
      }
    }

    if (editingTemplate.value) {
      await adminAPI.updateTemplate(editingTemplate.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await adminAPI.createTemplate(data)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadTemplates()
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(template: any) {
  try {
    await ElMessageBox.confirm('确定要删除这个模板吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await adminAPI.deleteTemplate(template.id)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

function addVariable() {
  formData.value.variables.push({
    name: '',
    description: '',
    default_value: ''
  })
}

function removeVariable(index: number) {
  formData.value.variables.splice(index, 1)
}
</script>

<style scoped>
.admin-templates-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.search-bar {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.variables-editor {
  width: 100%;
}

.variable-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
</style>

