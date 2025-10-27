<template>
  <div class="admin-users-page">
    <Header />
    
    <div class="content">
      <el-card>
        <template #header>
          <div class="card-header">
            <h2>用户管理</h2>
            <el-button type="primary" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              创建用户
            </el-button>
          </div>
        </template>

        <div class="search-bar">
          <el-input v-model="searchText" placeholder="搜索用户名或邮箱" clearable @clear="loadUsers" style="width: 300px">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="filterRole" placeholder="角色筛选" clearable @change="loadUsers" style="width: 150px">
            <el-option label="全部" value="" />
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
          <el-button type="primary" @click="loadUsers">搜索</el-button>
        </div>

        <el-table :data="users" style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.role === 'admin'" type="success">管理员</el-tag>
              <el-tag v-else>用户</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.is_active" type="success">正常</el-tag>
              <el-tag v-else type="danger">禁用</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteUser(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadUsers"
          @size-change="loadUsers"
          style="margin-top: 20px; justify-content: flex-end"
        />
      </el-card>
    </div>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="userForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="userForm.password" type="password" :placeholder="isEdit ? '留空则不修改' : '请输入密码'" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="userForm.is_active" active-text="正常" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUser" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import Header from '@/components/Layout/Header.vue'

const loading = ref(false)
const users = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const filterRole = ref('')

const dialogVisible = ref(false)
const dialogTitle = ref('创建用户')
const isEdit = ref(false)
const submitting = ref(false)
const userForm = ref({
  id: 0,
  username: '',
  email: '',
  password: '',
  role: 'user',
  is_active: true
})

onMounted(() => {
  loadUsers()
})

async function loadUsers() {
  loading.value = true
  try {
    const response = await adminAPI.getUsers({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchText.value || undefined,
      role: filterRole.value || undefined
    }) as any

    users.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleString('zh-CN')
}

function showCreateDialog() {
  isEdit.value = false
  dialogTitle.value = '创建用户'
  userForm.value = {
    id: 0,
    username: '',
    email: '',
    password: '',
    role: 'user',
    is_active: true
  }
  dialogVisible.value = true
}

function editUser(user: any) {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  userForm.value = {
    id: user.id,
    username: user.username,
    email: user.email,
    password: '',
    role: user.role,
    is_active: user.is_active
  }
  dialogVisible.value = true
}

async function submitUser() {
  if (!userForm.value.username || !userForm.value.email) {
    ElMessage.error('请填写必填项')
    return
  }

  if (!isEdit.value && !userForm.value.password) {
    ElMessage.error('请输入密码')
    return
  }

  submitting.value = true

  try {
    if (isEdit.value) {
      const data: any = {
        email: userForm.value.email,
        role: userForm.value.role,
        is_active: userForm.value.is_active
      }
      if (userForm.value.password) {
        data.password = userForm.value.password
      }
      await adminAPI.updateUser(userForm.value.id, data)
      ElMessage.success('用户更新成功')
    } else {
      await adminAPI.createUser({
        username: userForm.value.username,
        email: userForm.value.email,
        password: userForm.value.password
      })
      ElMessage.success('用户创建成功')
    }

    dialogVisible.value = false
    await loadUsers()
  } catch (error: any) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function deleteUser(user: any) {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${user.username}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await adminAPI.deleteUser(user.id)
    ElMessage.success('用户删除成功')
    await loadUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.admin-users-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.content {
  flex: 1;
  padding: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}

.search-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
</style>

