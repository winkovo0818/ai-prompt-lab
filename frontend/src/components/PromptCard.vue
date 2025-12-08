<template>
  <el-card 
    class="prompt-card cursor-pointer hover:shadow-lg transition-shadow"
    @click="handleClick"
  >
    <!-- 顶部彩色装饰条 -->
    <div class="card-accent" :style="{ background: getAccentColor() }"></div>
    
    <div class="flex justify-between items-start mb-3">
      <h3 class="text-lg font-semibold text-gray-800 flex-1">{{ prompt.title }}</h3>
      <div class="flex items-center space-x-2">
        <el-icon 
          :class="prompt.is_favorite ? 'text-yellow-500' : 'text-gray-400'"
          class="cursor-pointer hover:scale-110 transition-transform favorite-icon"
          @click.stop="handleFavorite"
        >
          <StarFilled v-if="prompt.is_favorite" />
          <Star v-else />
        </el-icon>
        <el-dropdown @command="handleCommand" trigger="click" @click.stop>
          <el-icon class="cursor-pointer text-gray-500 hover:text-gray-700 more-icon">
            <MoreFilled />
          </el-icon>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="edit">
                <el-icon><Edit /></el-icon>
                编辑
              </el-dropdown-item>
              <el-dropdown-item command="duplicate">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-dropdown-item>
              <el-dropdown-item command="versions">
                <el-icon><Clock /></el-icon>
                版本历史
              </el-dropdown-item>
              <el-dropdown-item command="delete" divided>
                <el-icon><Delete /></el-icon>
                删除
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <p v-if="prompt.description" class="text-sm text-gray-600 mb-3 line-clamp-2">
      {{ prompt.description }}
    </p>

    <div class="flex flex-wrap gap-2 mb-3" v-if="prompt.tags && prompt.tags.length > 0">
      <el-tag 
        v-for="tag in prompt.tags.slice(0, 3)" 
        :key="tag" 
        size="small"
        class="tag-item"
      >
        {{ tag }}
      </el-tag>
      <el-tag v-if="prompt.tags.length > 3" size="small" class="tag-more">
        +{{ prompt.tags.length - 3 }}
      </el-tag>
    </div>

    <div class="card-footer">
      <div class="flex items-center space-x-3">
        <span class="version-badge">v{{ prompt.version }}</span>
        <span v-if="prompt.is_public" class="public-badge">
          <el-icon class="mr-1"><Link /></el-icon>
          公开
        </span>
        <span v-if="prompt.team_shared" class="team-badge">
          <el-icon class="mr-1"><UserFilled /></el-icon>
          {{ prompt.team_info?.team_name || '团队' }}
          <span class="permission-tag" :class="prompt.team_info?.permission">
            {{ prompt.team_info?.permission === 'edit' ? '可编辑' : '只读' }}
          </span>
        </span>
      </div>
      <span class="time-text">{{ formatRelativeTime(prompt.updated_at) }}</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { PromptItem } from '@/api'
import { formatRelativeTime } from '@/utils/format'

const props = defineProps<{
  prompt: PromptItem
}>()

const emit = defineEmits<{
  click: [prompt: PromptItem]
  favorite: [id: number]
  edit: [id: number]
  duplicate: [id: number]
  versions: [id: number]
  delete: [id: number]
}>()

function handleClick() {
  emit('click', props.prompt)
}

function handleFavorite() {
  emit('favorite', props.prompt.id)
}

function handleCommand(command: string) {
  switch (command) {
    case 'edit':
      emit('edit', props.prompt.id)
      break
    case 'duplicate':
      emit('duplicate', props.prompt.id)
      break
    case 'versions':
      emit('versions', props.prompt.id)
      break
    case 'delete':
      emit('delete', props.prompt.id)
      break
  }
}

// 根据 prompt ID 生成不同的强调色
function getAccentColor() {
  const colors = [
    'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', // 蓝色
    'linear-gradient(135deg, #10b981 0%, #059669 100%)', // 绿色
    'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', // 橙色
    'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)', // 紫色
    'linear-gradient(135deg, #ec4899 0%, #db2777 100%)', // 粉色
    'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)', // 青色
  ]
  return colors[props.prompt.id % colors.length]
}
</script>

<style scoped>
.prompt-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  background: white;
  overflow: hidden;
  position: relative;
}

.prompt-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1) !important;
  border-color: transparent;
}

.prompt-card :deep(.el-card__body) {
  padding: 0;
  padding-top: 1.25rem;
  padding-left: 1.25rem;
  padding-right: 1.25rem;
  padding-bottom: 1.25rem;
}

/* 顶部彩色装饰条 */
.card-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 12px 12px 0 0;
}

.favorite-icon {
  font-size: 20px;
}

.more-icon {
  font-size: 18px;
}

/* 底部信息栏 */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
  margin-top: 0.5rem;
  font-size: 0.75rem;
}

.version-badge {
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 600;
  color: #6b7280;
}

.public-badge {
  display: flex;
  align-items: center;
  color: #10b981;
  font-weight: 500;
}

.team-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: #409eff;
  font-weight: 500;
  background: #ecf5ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
}

.permission-tag {
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 0.65rem;
  font-weight: 600;
}

.permission-tag.view {
  background: #fef3c7;
  color: #92400e;
}

.permission-tag.edit {
  background: #d1fae5;
  color: #065f46;
}

.time-text {
  color: #9ca3af;
  font-weight: 500;
}

.text-lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
}

.font-semibold {
  font-weight: 600;
}

.text-gray-800 {
  color: #1e293b;
}

.text-sm {
  font-size: 0.875rem;
  line-height: 1.5rem;
}

.text-gray-600 {
  color: #475569;
}

.text-xs {
  font-size: 0.75rem;
  line-height: 1rem;
}

.text-gray-500 {
  color: #64748b;
}

.text-yellow-500 {
  color: #eab308;
}

.text-gray-400 {
  color: #94a3b8;
}

.text-gray-700 {
  color: #334155;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.5rem;
}

.cursor-pointer {
  cursor: pointer;
}

.flex {
  display: flex;
}

.flex-1 {
  flex: 1;
}

.flex-wrap {
  flex-wrap: wrap;
}

.items-start {
  align-items: flex-start;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.space-x-2 > * + * {
  margin-left: 0.5rem;
}

.space-x-3 > * + * {
  margin-left: 0.75rem;
}

.gap-2 {
  gap: 0.5rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mr-1 {
  margin-right: 0.25rem;
}

.hover\:shadow-lg:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.hover\:scale-110:hover {
  transform: scale(1.1);
}

.hover\:text-gray-700:hover {
  color: #334155;
}

.transition-shadow {
  transition-property: box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.transition-transform {
  transition-property: transform;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.tag-item {
  border-radius: 6px;
  font-weight: 500;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  color: #6b7280;
  transition: all 0.2s;
}

.tag-item:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

.tag-more {
  border-radius: 6px;
  font-weight: 600;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  border: 1px solid #93c5fd;
  color: #3b82f6;
}
</style>

