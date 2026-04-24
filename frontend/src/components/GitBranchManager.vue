<template>
  <div class="branch-manager">
    <div class="branch-selector">
      <el-dropdown @command="handleBranchChange" trigger="click">
        <el-button type="primary" plain>
          <span>{{ currentBranch?.name || '选择分支' }}</span>
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-for="branch in branches" :key="branch.id" :command="branch.id">
              <div class="branch-item">
                <span class="branch-name">{{ branch.name }}</span>
                <el-tag v-if="branch.is_default" size="small" type="success">默认</el-tag>
              </div>
            </el-dropdown-item>
            <el-dropdown-item divided @click="showCreateDialog = true">
              <el-icon><plus /></el-icon>
              创建新分支
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 创建分支对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建新分支" width="400px">
      <el-form :model="newBranchForm" label-width="80px">
        <el-form-item label="分支名称">
          <el-input v-model="newBranchForm.name" placeholder="如: feature-new-prompt" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newBranchForm.description" type="textarea" placeholder="分支说明" />
        </el-form-item>
        <el-form-item label="基于">
          <el-select v-model="newBranchForm.base_branch_id" placeholder="选择基准分支" clearable>
            <el-option v-for="b in branches" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateBranch">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ArrowDown, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getBranches, createBranch, switchBranch } from '@/api/git'

const props = defineProps<{
  promptId: number
  modelValue?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
  (e: 'branch-changed', branch: any): void
}>()

const branches = ref<any[]>([])
const showCreateDialog = ref(false)
const newBranchForm = ref({ name: '', description: '', base_branch_id: null as number | null })

const currentBranch = computed(() =>
  branches.value.find(b => b.id === props.modelValue)
)

const loadBranches = async () => {
  try {
    const res = await getBranches(props.promptId)
    branches.value = res.data || []

    // 如果没有选择分支，默认选中第一个
    if (!props.modelValue && branches.value.length > 0) {
      emit('update:modelValue', branches.value[0].id)
    }
  } catch (err) {
    console.error('加载分支失败', err)
  }
}

const handleBranchChange = async (branchId: number) => {
  try {
    const res = await switchBranch(props.promptId, branchId)
    emit('update:modelValue', branchId)
    emit('branch-changed', res.data)
    ElMessage.success('已切换分支')
  } catch (err) {
    console.error('切换分支失败', err)
  }
}

const handleCreateBranch = async () => {
  if (!newBranchForm.value.name) {
    ElMessage.warning('请输入分支名称')
    return
  }
  try {
    const res = await createBranch(props.promptId, newBranchForm.value)
    branches.value.push(res.data)
    emit('update:modelValue', res.data.id)
    showCreateDialog.value = false
    newBranchForm.value = { name: '', description: '', base_branch_id: null }
    ElMessage.success('分支创建成功')
  } catch (err) {
    console.error('创建分支失败', err)
  }
}

onMounted(() => {
  loadBranches()
})

defineExpose({ loadBranches })
</script>

<style scoped>
.branch-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.branch-name {
  font-weight: 500;
}
</style>