<template>
  <div class="prompt-comments">
    <!-- 评论统计 -->
    <div class="comments-header">
      <div class="stats-bar">
        <span class="stat-item">
          <el-icon><ChatDotRound /></el-icon>
          {{ stats.total }} 条评论
        </span>
        <span v-if="stats.reviews > 0" class="stat-item">
          <el-icon><DocumentChecked /></el-icon>
          {{ stats.reviews }} 条评审
        </span>
        <span v-if="stats.pending_reviews > 0" class="stat-item pending">
          <el-icon><Clock /></el-icon>
          {{ stats.pending_reviews }} 待处理
        </span>
      </div>
      <div class="filter-bar">
        <el-select v-model="filterType" size="small" style="width: 120px">
          <el-option value="" label="全部" />
          <el-option value="comment" label="评论" />
          <el-option value="review" label="版本评审" />
          <el-option value="suggestion" label="建议" />
        </el-select>
        <el-select 
          v-if="versions.length > 0" 
          v-model="filterVersion" 
          size="small" 
          style="width: 120px"
          clearable
          placeholder="筛选版本"
        >
          <el-option 
            v-for="v in versions" 
            :key="v" 
            :value="v" 
            :label="`版本 ${v}`" 
          />
        </el-select>
      </div>
    </div>

    <!-- 发表评论 -->
    <div class="new-comment">
      <el-avatar :size="36" :src="currentUser?.avatar_url">
        <el-icon><User /></el-icon>
      </el-avatar>
      <div class="comment-input-wrapper">
        <div class="input-area">
          <el-input
            ref="commentInputRef"
            v-model="newComment"
            type="textarea"
            :rows="2"
            placeholder="发表评论... 输入 @ 可提及用户"
            @input="handleInput"
            @keydown="handleKeydown"
          />
          <!-- @提及用户下拉 -->
          <div v-if="showMentionList" class="mention-dropdown">
            <div 
              v-for="(user, index) in mentionUsers" 
              :key="user.id"
              class="mention-item"
              :class="{ active: mentionIndex === index }"
              @click="selectMention(user)"
            >
              <el-avatar :size="24" :src="user.avatar_url">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span>{{ user.username }}</span>
            </div>
            <div v-if="mentionUsers.length === 0" class="mention-empty">
              未找到用户
            </div>
          </div>
        </div>
        <div class="comment-actions">
          <el-select v-model="newCommentType" size="small" style="width: 100px">
            <el-option value="comment" label="评论" />
            <el-option value="review" label="版本评审" />
            <el-option value="suggestion" label="建议" />
          </el-select>
          <el-select 
            v-if="newCommentType === 'review' && versions.length > 0"
            v-model="newCommentVersion"
            size="small"
            style="width: 100px"
            placeholder="选择版本"
          >
            <el-option 
              v-for="v in versions" 
              :key="v" 
              :value="v" 
              :label="`版本 ${v}`" 
            />
          </el-select>
          <el-button 
            type="primary" 
            size="small" 
            @click="submitComment"
            :loading="submitting"
            :disabled="!newComment.trim()"
          >
            发表
          </el-button>
        </div>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="comments-list" v-loading="loading">
      <div 
        v-for="comment in filteredComments" 
        :key="comment.id" 
        class="comment-item"
        :class="{ 'is-review': comment.comment_type === 'review' }"
      >
        <el-avatar :size="36" :src="comment.avatar_url">
          <el-icon><User /></el-icon>
        </el-avatar>
        <div class="comment-content">
          <div class="comment-header">
            <span class="username">{{ comment.username }}</span>
            <el-tag 
              v-if="comment.comment_type === 'review'" 
              size="small" 
              type="warning"
            >
              版本 {{ comment.version }} 评审
            </el-tag>
            <el-tag 
              v-if="comment.comment_type === 'suggestion'" 
              size="small" 
              type="info"
            >
              建议
            </el-tag>
            <el-tag 
              v-if="comment.review_status === 'pending'" 
              size="small" 
              type="warning"
            >
              待处理
            </el-tag>
            <el-tag 
              v-if="comment.review_status === 'approved'" 
              size="small" 
              type="success"
            >
              已通过
            </el-tag>
            <el-tag 
              v-if="comment.review_status === 'rejected'" 
              size="small" 
              type="danger"
            >
              已拒绝
            </el-tag>
            <span class="time">{{ formatTime(comment.created_at) }}</span>
            <span v-if="comment.is_edited" class="edited">(已编辑)</span>
          </div>
          <div class="comment-body" v-html="renderContent(comment.content, comment.mentioned_users)"></div>
          <div class="comment-footer">
            <el-button text size="small" @click="startReply(comment)">
              <el-icon><ChatRound /></el-icon>
              回复
            </el-button>
            <template v-if="comment.comment_type === 'review' && comment.review_status === 'pending' && isOwner">
              <el-button text size="small" type="success" @click="updateReviewStatus(comment, 'approved')">
                <el-icon><Select /></el-icon>
                通过
              </el-button>
              <el-button text size="small" type="danger" @click="updateReviewStatus(comment, 'rejected')">
                <el-icon><CloseBold /></el-icon>
                拒绝
              </el-button>
            </template>
            <el-button 
              v-if="comment.user_id === currentUser?.id" 
              text 
              size="small" 
              @click="startEdit(comment)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              v-if="comment.user_id === currentUser?.id || currentUser?.role === 'admin'" 
              text 
              size="small"
              class="delete-btn"
              @click="deleteComment(comment)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>

          <!-- 回复列表 -->
          <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
            <div 
              v-for="reply in comment.replies" 
              :key="reply.id" 
              class="reply-item"
            >
              <el-avatar :size="28" :src="reply.avatar_url">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="reply-content">
                <div class="reply-header">
                  <span class="username">{{ reply.username }}</span>
                  <span class="time">{{ formatTime(reply.created_at) }}</span>
                </div>
                <div class="reply-body" v-html="renderContent(reply.content, reply.mentioned_users)"></div>
              </div>
            </div>
          </div>

          <!-- 回复输入框 -->
          <div v-if="replyingTo === comment.id" class="reply-input">
            <el-input
              v-model="replyContent"
              type="textarea"
              :rows="2"
              :placeholder="`回复 @${comment.username}...`"
              @input="handleInput"
            />
            <div class="reply-actions">
              <el-button size="small" @click="replyingTo = null">取消</el-button>
              <el-button 
                type="primary" 
                size="small" 
                @click="submitReply(comment)"
                :loading="submitting"
              >
                回复
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <el-empty v-if="!loading && filteredComments.length === 0" description="暂无评论" />
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑评论" width="500px">
      <el-input
        v-model="editContent"
        type="textarea"
        :rows="4"
      />
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { commentAPI, PromptComment, CommentUser, CommentStats } from '@/api'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ChatDotRound, DocumentChecked, Clock, User, ChatRound, 
  Edit, Delete, Select, CloseBold 
} from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  promptId: number
  versions?: number[]
  isOwner?: boolean
}>(), {
  versions: () => [],
  isOwner: false
})

const userStore = useUserStore()
const currentUser = computed(() => userStore.userInfo)

const loading = ref(false)
const submitting = ref(false)
const comments = ref<PromptComment[]>([])
const stats = ref<CommentStats>({
  total: 0, comments: 0, reviews: 0, suggestions: 0,
  pending_reviews: 0, approved_reviews: 0, rejected_reviews: 0
})

// 筛选
const filterType = ref('')
const filterVersion = ref<number | null>(null)

// 新评论
const newComment = ref('')
const newCommentType = ref<'comment' | 'review' | 'suggestion'>('comment')
const newCommentVersion = ref<number | null>(null)
const mentionedUserIds = ref<number[]>([])

// @提及
const showMentionList = ref(false)
const mentionUsers = ref<CommentUser[]>([])
const mentionIndex = ref(0)
const mentionStart = ref(0)
const commentInputRef = ref()

// 回复
const replyingTo = ref<number | null>(null)
const replyContent = ref('')

// 编辑
const editDialogVisible = ref(false)
const editContent = ref('')
const editingComment = ref<PromptComment | null>(null)

// 筛选后的评论
const filteredComments = computed(() => {
  let result = comments.value
  if (filterType.value) {
    result = result.filter(c => c.comment_type === filterType.value)
  }
  if (filterVersion.value !== null) {
    result = result.filter(c => c.version === filterVersion.value)
  }
  return result
})

// 加载评论
async function loadComments() {
  if (!props.promptId) return
  loading.value = true
  try {
    const [commentsRes, statsRes] = await Promise.all([
      commentAPI.getComments(props.promptId) as any,
      commentAPI.getStats(props.promptId) as any
    ])
    if (commentsRes.data) {
      comments.value = commentsRes.data
    }
    if (statsRes.data) {
      stats.value = statsRes.data
    }
  } catch (error) {
    console.error('加载评论失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理输入（检测@）
async function handleInput(value: string) {
  const input = commentInputRef.value?.$el?.querySelector('textarea') || 
                document.activeElement as HTMLTextAreaElement
  if (!input) return
  
  const cursorPos = input.selectionStart
  const textBefore = value.substring(0, cursorPos)
  const atMatch = textBefore.match(/@(\w*)$/)
  
  if (atMatch) {
    mentionStart.value = cursorPos - atMatch[1].length
    const keyword = atMatch[1]
    try {
      // 传递 promptId 来搜索团队成员，空关键词也搜索
      const res = await commentAPI.searchUsers(keyword || '', props.promptId) as any
      mentionUsers.value = res.data || []
      showMentionList.value = mentionUsers.value.length > 0
      mentionIndex.value = 0
    } catch (e) {
      mentionUsers.value = []
      showMentionList.value = false
    }
  } else {
    showMentionList.value = false
  }
}

// 键盘导航
function handleKeydown(e: KeyboardEvent) {
  if (!showMentionList.value) return
  
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    mentionIndex.value = Math.min(mentionIndex.value + 1, mentionUsers.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    mentionIndex.value = Math.max(mentionIndex.value - 1, 0)
  } else if (e.key === 'Enter' && mentionUsers.value.length > 0) {
    e.preventDefault()
    selectMention(mentionUsers.value[mentionIndex.value])
  } else if (e.key === 'Escape') {
    showMentionList.value = false
  }
}

// 选择提及用户
function selectMention(user: CommentUser) {
  const before = newComment.value.substring(0, mentionStart.value - 1)
  const after = newComment.value.substring(mentionStart.value + (newComment.value.substring(mentionStart.value).match(/^\w*/)?.[0]?.length || 0))
  newComment.value = `${before}@${user.username} ${after}`
  
  if (!mentionedUserIds.value.includes(user.id)) {
    mentionedUserIds.value.push(user.id)
  }
  
  showMentionList.value = false
}

// 发表评论
async function submitComment() {
  if (!newComment.value.trim()) return
  
  submitting.value = true
  try {
    await commentAPI.createComment(props.promptId, {
      content: newComment.value,
      mentioned_user_ids: mentionedUserIds.value.length > 0 ? mentionedUserIds.value : undefined,
      comment_type: newCommentType.value,
      version: newCommentType.value === 'review' ? newCommentVersion.value || undefined : undefined,
      review_status: newCommentType.value === 'review' ? 'pending' : undefined
    })
    
    ElMessage.success('评论成功')
    newComment.value = ''
    mentionedUserIds.value = []
    await loadComments()
  } catch (error: any) {
    ElMessage.error(error.message || '评论失败')
  } finally {
    submitting.value = false
  }
}

// 开始回复
function startReply(comment: PromptComment) {
  replyingTo.value = comment.id
  replyContent.value = ''
}

// 提交回复
async function submitReply(parentComment: PromptComment) {
  if (!replyContent.value.trim()) return
  
  submitting.value = true
  try {
    await commentAPI.createComment(props.promptId, {
      content: replyContent.value,
      parent_id: parentComment.id,
      comment_type: 'comment'
    })
    
    ElMessage.success('回复成功')
    replyingTo.value = null
    replyContent.value = ''
    await loadComments()
  } catch (error: any) {
    ElMessage.error(error.message || '回复失败')
  } finally {
    submitting.value = false
  }
}

// 开始编辑
function startEdit(comment: PromptComment) {
  editingComment.value = comment
  editContent.value = comment.content
  editDialogVisible.value = true
}

// 保存编辑
async function saveEdit() {
  if (!editingComment.value || !editContent.value.trim()) return
  
  submitting.value = true
  try {
    await commentAPI.updateComment(editingComment.value.id, {
      content: editContent.value
    })
    
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    await loadComments()
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    submitting.value = false
  }
}

// 删除评论
async function deleteComment(comment: PromptComment) {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '删除确认', {
      type: 'warning'
    })
    
    await commentAPI.deleteComment(comment.id)
    ElMessage.success('删除成功')
    await loadComments()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 更新评审状态
async function updateReviewStatus(comment: PromptComment, status: 'approved' | 'rejected') {
  try {
    await commentAPI.updateComment(comment.id, {
      review_status: status
    })
    
    ElMessage.success(status === 'approved' ? '已通过评审' : '已拒绝评审')
    await loadComments()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

// 渲染内容（高亮@提及）
function renderContent(content: string, mentionedUsers?: CommentUser[]) {
  if (!mentionedUsers || mentionedUsers.length === 0) {
    return content
  }
  
  let result = content
  for (const user of mentionedUsers) {
    const regex = new RegExp(`@${user.username}\\b`, 'g')
    result = result.replace(regex, `<span class="mention">@${user.username}</span>`)
  }
  return result
}

// 格式化时间
function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  
  return date.toLocaleDateString()
}

watch(() => props.promptId, () => {
  if (props.promptId) {
    loadComments()
  }
}, { immediate: true })

onMounted(() => {
  if (props.promptId) {
    loadComments()
  }
})
</script>

<style scoped>
.prompt-comments {
  padding: 0;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.stats-bar {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.stat-item .el-icon {
  font-size: 14px;
}

.stat-item.pending {
  color: #e6a23c;
}

.filter-bar {
  display: flex;
  gap: 8px;
}

.filter-bar :deep(.el-select .el-input__wrapper) {
  box-shadow: none;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
}

/* 新评论 */
.new-comment {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: #fafbfc;
  border-radius: 10px;
  border: 1px solid #ebeef5;
}

.new-comment :deep(.el-avatar) {
  flex-shrink: 0;
}

.comment-input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-area {
  position: relative;
}

.input-area :deep(.el-textarea__inner) {
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  padding: 10px 12px;
  font-size: 14px;
  transition: all 0.2s;
  background: #fff;
}

.input-area :deep(.el-textarea__inner:focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.mention-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 100;
}

.mention-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
}

.mention-item:hover,
.mention-item.active {
  background: #f5f7fa;
}

.mention-empty {
  padding: 0.75rem;
  text-align: center;
  color: #909399;
  font-size: 0.85rem;
}

.comment-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.75rem;
}

.comment-actions :deep(.el-select) {
  width: auto !important;
}

.comment-actions :deep(.el-select .el-input__wrapper) {
  border-radius: 6px;
  box-shadow: none;
  border: 1px solid #e4e7ed;
}

.comment-actions :deep(.el-button--primary) {
  border-radius: 6px;
  padding: 8px 20px;
}

/* 评论列表 */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 16px 0;
  background: transparent;
  border-bottom: 1px solid #f0f2f5;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-item.is-review {
  padding-left: 12px;
  border-left: 3px solid #e6a23c;
  background: #fffbf0;
  margin: 8px 0;
  border-radius: 0 8px 8px 0;
}

.comment-item :deep(.el-avatar) {
  flex-shrink: 0;
}

.comment-content {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.username {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.time {
  font-size: 12px;
  color: #c0c4cc;
}

.edited {
  font-size: 11px;
  color: #c0c4cc;
  font-style: italic;
}

.comment-body {
  color: #606266;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
}

.comment-body :deep(.mention) {
  color: #409eff;
  font-weight: 500;
  background: #ecf5ff;
  padding: 0 4px;
  border-radius: 4px;
}

.comment-footer {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  opacity: 0;
  transition: opacity 0.2s;
}

.comment-item:hover .comment-footer {
  opacity: 1;
}

.comment-footer :deep(.el-button) {
  padding: 4px 10px;
  font-size: 12px;
  color: #909399;
  border-radius: 4px;
  border: none;
  background: transparent;
}

.comment-footer :deep(.el-button:hover) {
  color: #409eff;
  background: #ecf5ff;
}

.comment-footer .delete-btn:hover {
  color: #f56c6c !important;
  background: #fef0f0 !important;
}

/* 回复列表 */
.replies-list {
  margin-top: 1rem;
  padding-left: 1rem;
  border-left: 2px solid #e4e7ed;
}

.reply-item {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 0;
}

.reply-item + .reply-item {
  border-top: 1px solid #f0f0f0;
}

.reply-content {
  flex: 1;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.reply-body {
  font-size: 0.9rem;
  color: #606266;
}

/* 回复输入 */
.reply-input {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 6px;
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
</style>
