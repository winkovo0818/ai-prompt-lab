/**
 * Prompt Git API - 分支、提交、PR 相关接口
 */
import request from './request'

// ============================================
// 分支管理
// ============================================

/**
 * 获取分支列表
 */
export function getBranches(promptId: number) {
  return request({
    url: `/api/prompt/${promptId}/branches`,
    method: 'get'
  })
}

/**
 * 创建分支
 */
export function createBranch(promptId: number, data: {
  name: string
  description?: string
  base_branch_id?: number
}) {
  return request({
    url: `/api/prompt/${promptId}/branches`,
    method: 'post',
    data
  })
}

/**
 * 切换分支
 */
export function switchBranch(promptId: number, branchId: number) {
  return request({
    url: `/api/prompt/${promptId}/branches/${branchId}/switch`,
    method: 'patch'
  })
}

/**
 * 删除分支
 */
export function deleteBranch(promptId: number, branchId: number) {
  return request({
    url: `/api/prompt/${promptId}/branches/${branchId}`,
    method: 'delete'
  })
}

// ============================================
// 提交管理
// ============================================

/**
 * 获取提交历史
 */
export function getCommits(promptId: number, branchId: number, page = 1, pageSize = 20) {
  return request({
    url: `/api/prompt/${promptId}/commits`,
    method: 'get',
    params: { branch_id: branchId, page, page_size: pageSize }
  })
}

/**
 * 创建提交（保存新版本）
 */
export function createCommit(promptId: number, data: {
  branch_id: number
  title: string
  content: string
  variables_schema?: Record<string, any>
}) {
  return request({
    url: `/api/prompt/${promptId}/commits`,
    method: 'post',
    data
  })
}

/**
 * 获取特定提交详情
 */
export function getCommit(promptId: number, commitId: number) {
  return request({
    url: `/api/prompt/${promptId}/commits/${commitId}`,
    method: 'get'
  })
}

/**
 * 回滚到指定版本
 */
export function revertCommit(promptId: number, branchId: number, commitId: number) {
  return request({
    url: `/api/prompt/${promptId}/commits/revert`,
    method: 'post',
    params: { branch_id: branchId, commit_id: commitId }
  })
}

// ============================================
// Diff 对比
// ============================================

/**
 * 计算两版本差异
 */
export function getDiff(promptId: number, fromCommit: number, toCommit: number) {
  return request({
    url: `/api/prompt/${promptId}/diff`,
    method: 'get',
    params: { from_commit: fromCommit, to_commit: toCommit }
  })
}

/**
 * 获取 unified diff 格式
 */
export function getUnifiedDiff(promptId: number, fromCommit: number, toCommit: number) {
  return request({
    url: `/api/prompt/${promptId}/diff/unified`,
    method: 'get',
    params: { from_commit: fromCommit, to_commit: toCommit }
  })
}

// ============================================
// Pull Request
// ============================================

/**
 * 获取 PR 列表
 */
export function getPullRequests(promptId: number, status?: string, page = 1, pageSize = 10) {
  return request({
    url: `/api/prompt/${promptId}/pull-requests`,
    method: 'get',
    params: { status, page, page_size: pageSize }
  })
}

/**
 * 创建 PR
 */
export function createPullRequest(promptId: number, data: {
  source_branch_id: number
  target_branch_id: number
  title: string
  description?: string
}) {
  return request({
    url: `/api/prompt/${promptId}/pull-requests`,
    method: 'post',
    data
  })
}

/**
 * 获取 PR 详情
 */
export function getPullRequest(promptId: number, prId: number) {
  return request({
    url: `/api/prompt/${promptId}/pull-requests/${prId}`,
    method: 'get'
  })
}

/**
 * 合并 PR
 */
export function mergePullRequest(promptId: number, prId: number, mergeMethod = 'squash') {
  return request({
    url: `/api/prompt/${promptId}/pull-requests/${prId}/merge`,
    method: 'post',
    params: { merge_method: mergeMethod }
  })
}

/**
 * 关闭 PR
 */
export function closePullRequest(promptId: number, prId: number) {
  return request({
    url: `/api/prompt/${promptId}/pull-requests/${prId}/close`,
    method: 'post'
  })
}

/**
 * 更新 PR 审核人
 */
export function updatePRReviewer(promptId: number, prId: number, reviewerId?: number) {
  return request({
    url: `/api/prompt/${promptId}/pull-requests/${prId}/reviewers`,
    method: 'patch',
    data: { reviewer_id: reviewerId }
  })
}