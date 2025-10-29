<template>
  <div class="templates-page">
    <Header />
    
    <div class="content-container">
      <div class="main-content p-6">
      <!-- 页面标题 -->
      <div class="page-header mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">
          Prompt 模板库
        </h1>
        <p class="text-gray-600">精选优质模板，快速上手 AI 应用</p>
      </div>

    <!-- 搜索和筛选栏 -->
    <div class="filter-section">
      <div class="flex flex-wrap gap-4">
        <!-- 搜索框 -->
        <el-input
          v-model="searchKeyword"
          placeholder="搜索模板..."
          prefix-icon="Search"
          clearable
          class="flex-1 min-w-[200px]"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        />

        <!-- 分类筛选 -->
        <el-select
          v-model="selectedCategory"
          placeholder="选择分类"
          clearable
          class="w-48"
          @change="handleCategoryChange"
        >
          <el-option
            v-for="category in topCategories"
            :key="category.id"
            :label="`${category.icon} ${category.name}`"
            :value="category.id"
          />
        </el-select>

        <!-- 子分类筛选 -->
        <el-select
          v-if="subCategories.length > 0"
          v-model="selectedSubCategory"
          placeholder="选择子分类"
          clearable
          class="w-48"
          @change="loadTemplates"
        >
          <el-option
            v-for="category in subCategories"
            :key="category.id"
            :label="`${category.icon} ${category.name}`"
            :value="category.id"
          />
        </el-select>

        <!-- 难度筛选 -->
        <el-select
          v-model="selectedDifficulty"
          placeholder="难度级别"
          clearable
          class="w-32"
          @change="loadTemplates"
        >
          <el-option label="🟢 入门" value="beginner" />
          <el-option label="🟡 中级" value="intermediate" />
          <el-option label="🔴 高级" value="advanced" />
        </el-select>

        <!-- 仅看精选 -->
        <el-checkbox
          v-model="onlyFeatured"
          @change="loadTemplates"
        >
          ⭐ 仅看精选
        </el-checkbox>

        <!-- 搜索按钮 -->
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>

      <!-- 快捷分类标签 -->
      <div class="flex flex-wrap gap-2 mt-3">
        <el-tag
          v-for="category in featuredCategories"
          :key="category.id"
          :type="selectedCategory === category.id ? 'primary' : ''"
          size="large"
          class="cursor-pointer"
          @click="selectCategory(category.id)"
        >
          {{ category.icon }} {{ category.name }} ({{ category.template_count }})
        </el-tag>
      </div>
    </div>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="mb-4" @tab-change="handleTabChange">
      <el-tab-pane label="全部模板" name="all">
        <template #label>
          <span><el-icon><Grid /></el-icon> 全部模板 {{ total > 0 ? `(${total})` : '' }}</span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="我的收藏" name="favorites">
        <template #label>
          <span><el-icon><Star /></el-icon> 我的收藏</span>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- 模板列表 -->
    <div v-loading="loading" class="templates-grid">
      <el-card
        v-for="template in templates"
        :key="template.id"
        class="template-card"
        shadow="hover"
        @click="showTemplateDetail(template.id)"
      >
        <!-- 标题和徽章 -->
        <div class="flex items-start justify-between mb-3">
          <h3 class="card-title flex-1">{{ template.title }}</h3>
          <div class="flex gap-1">
            <el-tag v-if="template.is_featured" type="warning" size="small">⭐精选</el-tag>
            <el-tag v-if="template.is_official" type="success" size="small">✓官方</el-tag>
          </div>
        </div>

        <!-- 描述 -->
        <p class="card-description">{{ template.description || '暂无描述' }}</p>
        
        <!-- 标签 -->
        <div class="flex flex-wrap gap-2 mb-3">
          <el-tag
            v-for="tag in template.tags?.slice(0, 3)"
            :key="tag"
            size="small"
            type="info"
          >
            {{ tag }}
          </el-tag>
        </div>

        <!-- 底部信息 -->
        <div class="flex items-center justify-between text-sm text-gray-500">
          <div class="flex items-center gap-3">
            <span><el-icon><View /></el-icon> {{ template.use_count }}</span>
            <span><el-icon><Star /></el-icon> {{ template.favorite_count }}</span>
            <el-rate
              :model-value="template.rating"
              disabled
              size="small"
              show-score
              text-color="#ff9900"
            />
          </div>
          <el-tag :type="getDifficultyType(template.difficulty)" size="small">
            {{ getDifficultyText(template.difficulty) }}
          </el-tag>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!loading && templates.length === 0"
      description="暂无模板"
      :image-size="200"
    />

    <!-- 分页 -->
    <div v-if="total > 0" class="flex justify-center mt-6">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="loadTemplates"
        @size-change="loadTemplates"
      />
    </div>

    <!-- 模板详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentTemplate?.title"
      width="800px"
      destroy-on-close
    >
      <div v-if="currentTemplate" v-loading="detailLoading">
        <!-- 描述 -->
        <div class="mb-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">📝 描述</h4>
          <p class="text-gray-600">{{ currentTemplate.description || '暂无描述' }}</p>
        </div>

        <!-- 标签和难度 -->
        <div class="flex items-center gap-4 mb-4">
          <div class="flex gap-2">
            <el-tag
              v-for="tag in currentTemplate.tags"
              :key="tag"
              size="small"
            >
              {{ tag }}
            </el-tag>
          </div>
          <el-tag :type="getDifficultyType(currentTemplate.difficulty)" size="small">
            {{ getDifficultyText(currentTemplate.difficulty) }}
          </el-tag>
        </div>

        <!-- Prompt 内容 -->
        <div class="mb-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">💬 Prompt 内容</h4>
          <div class="bg-gray-50 rounded p-4 text-sm font-mono whitespace-pre-wrap">
            {{ currentTemplate.content }}
          </div>
        </div>

        <!-- 变量说明 -->
        <div v-if="currentTemplate.variables && currentTemplate.variables.length > 0" class="mb-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">🔧 变量说明</h4>
          <el-table :data="currentTemplate.variables" size="small" border>
            <el-table-column prop="name" label="变量名" width="150" />
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="default" label="默认值" width="150" />
          </el-table>
        </div>

        <!-- 示例 -->
        <div v-if="currentTemplate.example_output" class="mb-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">💡 示例输出</h4>
          <div class="bg-blue-50 rounded p-4 text-sm">
            {{ currentTemplate.example_output }}
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="flex items-center gap-6 mb-4 text-sm text-gray-600">
          <span>
            <el-icon><View /></el-icon>
            使用 {{ currentTemplate.use_count }} 次
          </span>
          <span>
            <el-icon><Star /></el-icon>
            收藏 {{ currentTemplate.favorite_count }} 次
          </span>
          <div class="flex items-center gap-2">
            <el-rate
              :model-value="currentTemplate.rating"
              disabled
              size="small"
            />
            <span>{{ currentTemplate.rating.toFixed(1) }} ({{ currentTemplate.rating_count || 0 }}人评分)</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex gap-3">
          <el-button type="primary" size="large" @click="useTemplate(currentTemplate.id)">
            <el-icon><DocumentCopy /></el-icon>
            使用这个模板
          </el-button>
          <el-button
            :type="currentTemplate.is_favorited ? 'warning' : 'default'"
            size="large"
            @click="toggleFavorite(currentTemplate.id)"
          >
            <el-icon><Star /></el-icon>
            {{ currentTemplate.is_favorited ? '取消收藏' : '收藏' }}
          </el-button>
          <el-button size="large" @click="showRatingDialog">
            <el-icon><StarFilled /></el-icon>
            评分
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 评分对话框 -->
    <el-dialog
      v-model="ratingDialogVisible"
      title="给模板评分"
      width="500px"
    >
      <div class="text-center">
        <el-rate
          v-model="ratingForm.rating"
          size="large"
          :texts="['很差', '较差', '一般', '不错', '很棒']"
          show-text
        />
        <el-input
          v-model="ratingForm.comment"
          type="textarea"
          :rows="4"
          placeholder="说说你的使用体验（可选）"
          class="mt-4"
          maxlength="500"
          show-word-limit
        />
      </div>
      <template #footer>
        <el-button @click="ratingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRating">提交评分</el-button>
      </template>
    </el-dialog>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Grid, Star, View, DocumentCopy, StarFilled } from '@element-plus/icons-vue'
import { templateAPI, type TemplateCategory, type TemplateListItem, type PromptTemplate } from '@/api'
import Header from '@/components/Layout/Header.vue'

const router = useRouter()

// 数据
const categories = ref<TemplateCategory[]>([])
const templates = ref<TemplateListItem[]>([])
const currentTemplate = ref<PromptTemplate | null>(null)

// 筛选条件
const searchKeyword = ref('')
const selectedCategory = ref<number | undefined>(undefined)
const selectedSubCategory = ref<number | undefined>(undefined)
const selectedDifficulty = ref<string | undefined>(undefined)
const onlyFeatured = ref(false)
const activeTab = ref('all')

// 分页
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 加载状态
const loading = ref(false)
const detailLoading = ref(false)

// 对话框
const detailDialogVisible = ref(false)
const ratingDialogVisible = ref(false)

// 评分表单
const ratingForm = ref({
  rating: 5,
  comment: ''
})

// 计算属性
const topCategories = computed(() => {
  return categories.value.filter(c => !c.parent_id)
})

const subCategories = computed(() => {
  if (!selectedCategory.value) return []
  return categories.value.filter(c => c.parent_id === selectedCategory.value)
})

const featuredCategories = computed(() => {
  return topCategories.value.slice(0, 8)
})

// 方法
const loadCategories = async () => {
  try {
    const res = await templateAPI.getCategories() as any
    categories.value = res.data
  } catch (error: any) {
    ElMessage.error(error.message || '加载分类失败')
  }
}

const loadTemplates = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (activeTab.value === 'all') {
      if (selectedSubCategory.value) {
        params.category_id = selectedSubCategory.value
      } else if (selectedCategory.value) {
        params.category_id = selectedCategory.value
      }
      if (selectedDifficulty.value) {
        params.difficulty = selectedDifficulty.value
      }
      if (searchKeyword.value) {
        params.search = searchKeyword.value
      }
      if (onlyFeatured.value) {
        params.is_featured = true
      }
      const res = await templateAPI.getList(params) as any
      templates.value = res.data.items
      total.value = res.data.total
    } else {
      // 收藏列表
      const res = await templateAPI.getFavorites({
        page: currentPage.value,
        page_size: pageSize.value
      }) as any
      templates.value = res.data.items
      total.value = res.data.total
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载模板失败')
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = () => {
  selectedSubCategory.value = undefined
  loadTemplates()
}

const selectCategory = (categoryId: number) => {
  selectedCategory.value = categoryId
  selectedSubCategory.value = undefined
  loadTemplates()
}

const handleSearch = () => {
  currentPage.value = 1
  loadTemplates()
}

const handleTabChange = () => {
  currentPage.value = 1
  loadTemplates()
}

const showTemplateDetail = async (id: number) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  try {
    const res = await templateAPI.getDetail(id) as any
    currentTemplate.value = res.data
  } catch (error: any) {
    ElMessage.error(error.message || '加载模板详情失败')
  } finally {
    detailLoading.value = false
  }
}

const useTemplate = async (id: number) => {
  try {
    const res = await templateAPI.use(id) as any
    const promptId = res.data.prompt_id
    const variables = res.data.variables
    
    // 如果模板有变量配置，将默认值保存到 localStorage
    if (variables && variables.length > 0) {
      const defaultValues: Record<string, string> = {}
      variables.forEach((v: any) => {
        if (v.name && v.default_value) {
          defaultValues[v.name] = v.default_value
        }
      })
      
      // 保存到 localStorage（使用与编辑器相同的 key 格式）
      if (Object.keys(defaultValues).length > 0) {
        const cacheKey = `prompt_variables_${promptId}`
        localStorage.setItem(cacheKey, JSON.stringify(defaultValues))
        console.log('✅ 已保存变量默认值到缓存:', defaultValues)
      }
    }
    
    ElMessage.success('模板已复制到您的 Prompt 列表')
    detailDialogVisible.value = false
    // 跳转到编辑页面
    router.push(`/editor/${promptId}`)
  } catch (error: any) {
    ElMessage.error(error.message || '使用模板失败')
  }
}

const toggleFavorite = async (id: number) => {
  try {
    const res = await templateAPI.toggleFavorite(id) as any
    if (currentTemplate.value) {
      currentTemplate.value.is_favorited = res.data.is_favorited
    }
    // 更新列表中的状态
    const template = templates.value.find(t => t.id === id)
    if (template) {
      template.is_favorited = res.data.is_favorited
    }
    ElMessage.success(res.message || '操作成功')
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const showRatingDialog = () => {
  ratingForm.value = {
    rating: 5,
    comment: ''
  }
  ratingDialogVisible.value = true
}

const submitRating = async () => {
  if (!currentTemplate.value) return
  try {
    await templateAPI.rate(currentTemplate.value.id, ratingForm.value)
    ElMessage.success('评分成功')
    ratingDialogVisible.value = false
    // 重新加载模板详情
    showTemplateDetail(currentTemplate.value.id)
  } catch (error: any) {
    ElMessage.error(error.message || '评分失败')
  }
}

const getDifficultyType = (difficulty: string) => {
  const map: Record<string, any> = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'danger'
  }
  return map[difficulty] || 'info'
}

const getDifficultyText = (difficulty: string) => {
  const map: Record<string, string> = {
    beginner: '入门',
    intermediate: '中级',
    advanced: '高级'
  }
  return map[difficulty] || difficulty
}

// 生命周期
onMounted(() => {
  loadCategories()
  loadTemplates()
})
</script>

<style scoped>
/* 页面整体布局 */
.templates-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.content-container {
  flex: 1;
  overflow: hidden;
}

.main-content {
  height: 100%;
  overflow-y: auto;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.main-content::-webkit-scrollbar {
  width: 10px;
}

.main-content::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.main-content::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 5px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* 页面头部 */
.page-header {
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

/* 筛选区域 */
.filter-section {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e5e7eb;
}

/* 模板网格 */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.25rem;
  padding-bottom: 2rem;
}

/* 模板卡片 */
.template-card {
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  transform: translateY(-2px);
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-description {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.6;
  margin: 0.75rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 响应式 */
@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    padding: 1.5rem;
  }
  
  .stats-box {
    flex-direction: column;
    gap: 1rem;
  }
  
  .stat-divider {
    width: 100%;
    height: 1px;
  }
}
</style>

