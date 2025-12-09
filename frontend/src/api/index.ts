import request from './request'

// 类型定义
export interface APIResponse<T = any> {
  code: number
  data: T
  message: string
}

// Axios 拦截器处理后的响应类型
export interface InterceptedResponse<T = any> {
  data: T
  message: string
}

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface UserInfo {
  id: number
  username: string
  email: string
  avatar_url?: string
  api_key?: string
  role: string
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export interface PromptData {
  title: string
  content: string
  description?: string
  tags?: string[]
  is_public?: boolean
}

export interface PromptItem {
  id: number
  user_id?: number
  title: string
  content?: string
  description?: string
  tags?: string[]
  is_favorite: boolean
  is_public: boolean
  is_owner?: boolean
  version: number
  created_at: string
  updated_at: string
  // 团队共享信息
  team_shared?: boolean
  team_info?: {
    team_id: number
    team_name: string
    permission: string
  }
}

export interface RunPromptData {
  prompt_id?: number
  prompt_content?: string
  variables?: Record<string, string>
  file_variables?: Record<string, number>
  model?: string
  temperature?: number
  max_tokens?: number
}

export interface ABTestData {
  test_name: string
  prompt_ids: number[]
  input_variables?: Record<string, string>
  file_variables?: Record<string, number>
  model?: string
  api_base_url?: string
  api_key?: string
}

export interface AIConfigData {
  id?: number
  name: string
  base_url: string  // 注意：API 使用 snake_case
  api_key: string   // 注意：API 使用 snake_case
  model: string
  description?: string
}

export interface AIConfigResponse {
  id: number
  user_id: number
  name: string
  base_url: string
  api_key: string
  model: string
  description?: string
  is_global?: boolean
  is_default?: boolean
  created_at: string
  updated_at: string
}

export interface ExecutionHistoryItem {
  id: number
  user_id: number
  prompt_id?: number
  prompt_content: string
  prompt_version: number
  variables?: Record<string, string>
  final_prompt: string
  model: string
  temperature: number
  max_tokens: number
  output: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  cost: number
  response_time: number
  created_at: string
  is_cached: boolean
}

// 认证相关 API
export const authAPI = {
  // 注册
  register: (data: RegisterData) => 
    request.post<APIResponse<TokenResponse>>('/api/auth/register', data),
  
  // 登录
  login: (data: LoginData) => 
    request.post<APIResponse<TokenResponse>>('/api/auth/login', data),
  
  // 获取当前用户信息
  getCurrentUser: () => 
    request.get<APIResponse<UserInfo>>('/api/auth/me'),
  
  // 更新 API Key
  updateApiKey: (apiKey: string) => 
    request.put<APIResponse>('/api/auth/api-key', { api_key: apiKey }),
  
  // 更新个人资料
  updateProfile: (data: { email?: string, password?: string }) =>
    request.put<APIResponse<UserInfo>>('/api/auth/profile', data),
  
  // 上传头像
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<APIResponse<{ avatar_url: string }>>('/api/auth/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// 管理员 API
export const adminAPI = {
  // 用户管理
  getUsers: (params?: { skip?: number, limit?: number, search?: string, role?: string }) =>
    request.get<APIResponse<{ items: any[], total: number }>>('/api/admin/users', { params }),
  
  createUser: (data: { username: string, email: string, password: string }) =>
    request.post<APIResponse<UserInfo>>('/api/admin/users', data),
  
  updateUser: (userId: number, data: any) =>
    request.put<APIResponse<UserInfo>>(`/api/admin/users/${userId}`, data),
  
  deleteUser: (userId: number) =>
    request.delete<APIResponse>(`/api/admin/users/${userId}`),
  
  // Prompt管理
  getAllPrompts: (params?: { skip?: number, limit?: number, search?: string, user_id?: number }) =>
    request.get<APIResponse<{ items: any[], total: number }>>('/api/admin/prompts', { params }),
  
  deletePrompt: (promptId: number) =>
    request.delete<APIResponse>(`/api/admin/prompts/${promptId}`),
  
  togglePromptPublic: (promptId: number, isPublic: boolean) =>
    request.put<APIResponse>(`/api/admin/prompts/${promptId}/public`, { is_public: isPublic }),
  
  // 网站设置管理
  getSiteSettings: () =>
    request.get<APIResponse<any>>('/api/admin/site-settings'),
  
  updateSiteSettings: (data: any) =>
    request.put<APIResponse<any>>('/api/admin/site-settings', data),
  
  // 模板库管理
  createTemplate: (data: {
    category_id: number
    title: string
    description?: string
    content: string
    variables?: Array<{ name: string; description: string; default_value: string }>
    example_input?: any
    example_output?: string
    tags?: string[]
    difficulty?: string
    is_featured?: boolean
  }) =>
    request.post<APIResponse<{ id: number }>>('/api/admin/templates', data),
  
  updateTemplate: (templateId: number, data: any) =>
    request.put<APIResponse<{ id: number }>>(`/api/admin/templates/${templateId}`, data),
  
  deleteTemplate: (templateId: number) =>
    request.delete<APIResponse>(`/api/admin/templates/${templateId}`),
  
  // 团队管理
  getTeams: (params?: { skip?: number; limit?: number; search?: string }) =>
    request.get<APIResponse<{ items: any[]; total: number }>>('/api/admin/teams', { params }),
  
  getTeamDetail: (teamId: number) =>
    request.get<APIResponse<any>>(`/api/admin/teams/${teamId}`),
  
  updateTeam: (teamId: number, data: any) =>
    request.put<APIResponse<null>>(`/api/admin/teams/${teamId}`, data),
  
  deleteTeam: (teamId: number) =>
    request.delete<APIResponse<null>>(`/api/admin/teams/${teamId}`),
  
  removeTeamMember: (teamId: number, memberId: number) =>
    request.delete<APIResponse<null>>(`/api/admin/teams/${teamId}/members/${memberId}`)
}

// 网站公开 API
export const siteAPI = {
  // 获取网站公开设置（无需登录）
  getPublicSettings: () =>
    request.get<APIResponse<any>>('/api/site/settings')
}

// Prompt 管理 API
export const promptAPI = {
  // 创建 Prompt
  create: (data: PromptData) => 
    request.post<InterceptedResponse<PromptItem>>('/api/prompt', data),
  
  // 获取 Prompt 列表
  getList: (params?: {
    skip?: number
    limit?: number
    search?: string
    tags?: string
    is_favorite?: boolean
    is_public?: boolean
  }) => 
    request.get<InterceptedResponse<{ items: PromptItem[], total: number }>>('/api/prompt/list', { params }),
  
  // 获取 Prompt 详情
  getDetail: (id: number) => 
    request.get<InterceptedResponse<PromptItem>>(`/api/prompt/${id}`),
  
  // 更新 Prompt
  update: (id: number, data: Partial<PromptData>) => 
    request.put<InterceptedResponse<PromptItem>>(`/api/prompt/${id}`, data),
  
  // 删除 Prompt
  delete: (id: number) => 
    request.delete<InterceptedResponse<any>>(`/api/prompt/${id}`),
  
  // 获取版本历史
  getVersions: (id: number) => 
    request.get<InterceptedResponse<any[]>>(`/api/prompt/${id}/versions`),
  
  // 切换收藏
  toggleFavorite: (id: number) => 
    request.post<InterceptedResponse<{ is_favorite: boolean }>>(`/api/prompt/${id}/favorite`)
}

// 执行 API
export const runAPI = {
  // 执行 Prompt
  execute: (data: RunPromptData) => 
    request.post<APIResponse<any>>('/api/run', data),
  
  // 获取可用模型
  getModels: () => 
    request.get<APIResponse<any[]>>('/api/run/models'),
  
  // 获取使用统计
  getUsage: () => 
    request.get<APIResponse<any>>('/api/run/usage')
}

// A/B 测试 API
export const abtestAPI = {
  // 创建 A/B 测试
  create: (data: ABTestData & { enable_evaluation?: boolean, generate_report?: boolean }) => 
    request.post<APIResponse<any>>('/api/abtest', data),
  
  // 获取测试列表
  getList: (params?: { skip?: number, limit?: number }) => 
    request.get<APIResponse<{ items: any[], total: number }>>('/api/abtest/list', { params }),
  
  // 获取测试详情
  getDetail: (id: number) => 
    request.get<APIResponse<any>>(`/api/abtest/${id}`),
  
  // 删除测试
  delete: (id: number) => 
    request.delete<APIResponse>(`/api/abtest/${id}`),
  
  // 获取对比报告
  getReport: (id: number) => 
    request.get<APIResponse<any>>(`/api/abtest/${id}/report`),
  
  // 重新生成对比报告
  regenerateReport: (id: number) => 
    request.post<APIResponse<any>>(`/api/abtest/${id}/regenerate-report`)
}

// 批量测试 API
export const batchTestAPI = {
  // 创建批量测试
  create: (data: {
    test_name: string
    prompt_id: number
    test_cases: Array<{
      variables?: Record<string, string>
      expected_output?: string
    }>
    model?: string
    temperature?: number
    enable_evaluation?: boolean
  }) => 
    request.post<APIResponse<any>>('/api/batch-test', data),
  
  // 获取批量测试列表
  getList: (params?: { skip?: number, limit?: number }) => 
    request.get<APIResponse<{ items: any[], total: number }>>('/api/batch-test/list', { params }),
  
  // 获取批量测试详情
  getDetail: (id: number) => 
    request.get<APIResponse<any>>(`/api/batch-test/${id}`),
  
  // 删除批量测试
  delete: (id: number) => 
    request.delete<APIResponse>(`/api/batch-test/${id}`),
  
  // 导出测试报告
  export: (id: number) => 
    request.post<APIResponse<any>>(`/api/batch-test/${id}/export`)
}

// Prompt 优化 API
export const optimizationAPI = {
  // 分析并优化 Prompt
  analyze: (data: {
    prompt_content: string
    optimization_goals?: string[]
  }) => 
    request.post<APIResponse<{
      original_prompt: string
      optimized_prompt: string
      improvements: Array<{
        aspect: string
        before: string
        after: string
        reason: string
      }>
      optimization_suggestions: string[]
      expected_improvement: string
    }>>('/api/optimization/analyze', data)
}

// Prompt 分析 API（AI 智能分析）
export interface PromptAnalysisResult {
  overall_score: number
  dimensions: {
    clarity: { score: number; comment: string }
    structure: { score: number; comment: string }
    completeness: { score: number; comment: string }
    executability: { score: number; comment: string }
  }
  strengths: string[]
  weaknesses: string[]
  suggestions: Array<{
    type: string
    priority: string
    title: string
    description: string
    example?: string
  }>
  optimized_prompt: string
  best_practices: Array<{
    rule: string
    status: 'pass' | 'fail'
    message: string
  }>
}

export interface QuickAnalysisResult {
  quick_score: number
  tips: Array<{
    type: 'info' | 'warning' | 'suggestion'
    message: string
  }>
  variable_count: number
  character_count: number
  has_role: boolean
  has_format: boolean
  has_example: boolean
}

export const promptAnalysisAPI = {
  // AI 深度分析
  analyze: (data: { content: string; title?: string }) =>
    request.post<APIResponse<{
      success: boolean
      analysis: PromptAnalysisResult
      tokens_used?: number
    }>>('/api/prompt/analysis/analyze', data),
  
  // 快速本地分析（不调用 AI）
  quickAnalyze: (data: { content: string }) =>
    request.post<APIResponse<{
      success: boolean
      analysis: QuickAnalysisResult
    }>>('/api/prompt/analysis/quick', data)
}

// AI 配置 API
export const aiConfigAPI = {
  // 获取 AI 配置列表
  getList: () => 
    request.get<APIResponse<AIConfigResponse[]>>('/api/ai-config/list'),
  
  // 创建 AI 配置
  create: (data: AIConfigData) => 
    request.post<APIResponse<AIConfigResponse>>('/api/ai-config/create', data),
  
  // 更新 AI 配置
  update: (id: number, data: Partial<AIConfigData>) => 
    request.put<APIResponse<AIConfigResponse>>(`/api/ai-config/${id}`, data),
  
  // 删除 AI 配置
  delete: (id: number) => 
    request.delete<APIResponse<any>>(`/api/ai-config/${id}`),
  
  // 获取单个 AI 配置
  getDetail: (id: number) => 
    request.get<APIResponse<AIConfigResponse>>(`/api/ai-config/${id}`),
  
  // 测试 AI 配置连接
  test: (id: number) => 
    request.post<APIResponse<{
      status: string
      model: string
      response?: string
    }>>(`/api/ai-config/${id}/test`),
  
  // 测试连接（不保存配置）
  testConnection: (data: AIConfigData) => 
    request.post<APIResponse<{
      status: string
      model: string
      response?: string
    }>>('/api/ai-config/test-connection', data)
}

// 执行历史 API
export const executionHistoryAPI = {
  // 搜索执行历史记录（查找缓存）
  search: (params: {
    prompt_id?: number
    prompt_content?: string
    prompt_version?: number
    variables?: string  // JSON字符串
    model?: string
    temperature?: number
    max_tokens?: number
  }) => 
    request.get<APIResponse<ExecutionHistoryItem | null>>('/api/execution_history/search', { params }),
  
  // 获取执行历史列表
  getList: (params?: {
    prompt_id?: number
    skip?: number
    limit?: number
  }) => 
    request.get<APIResponse<{ items: ExecutionHistoryItem[], total: number }>>('/api/execution_history/list', { params }),
  
  // 删除执行历史
  delete: (id: number) => 
    request.delete<APIResponse<any>>(`/api/execution_history/${id}`)
}

// ============================================
// Prompt 模板相关
// ============================================

export interface TemplateCategory {
  id: number
  name: string
  name_en?: string
  description?: string
  icon: string
  parent_id?: number
  sort_order: number
  template_count?: number
}

export interface TemplateVariable {
  name: string
  description: string
  default?: string
}

export interface PromptTemplate {
  id: number
  category_id: number
  title: string
  description?: string
  content: string
  variables?: TemplateVariable[]
  example_input?: Record<string, string>
  example_output?: string
  tags?: string[]
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  use_count: number
  favorite_count: number
  rating: number
  rating_count?: number
  is_official: boolean
  is_featured: boolean
  is_favorited?: boolean
  created_at: string
}

export interface TemplateListItem {
  id: number
  category_id: number
  title: string
  description?: string
  tags?: string[]
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  use_count: number
  favorite_count: number
  rating: number
  is_official: boolean
  is_featured: boolean
  is_favorited?: boolean
}

export interface TemplateListResponse {
  items: TemplateListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const templateAPI = {
  // 获取所有分类
  getCategories: () => 
    request.get<APIResponse<TemplateCategory[]>>('/api/template/categories'),
  
  // 获取模板列表
  getList: (params?: {
    category_id?: number
    difficulty?: string
    search?: string
    is_featured?: boolean
    page?: number
    page_size?: number
  }) => 
    request.get<APIResponse<TemplateListResponse>>('/api/template/list', { params }),
  
  // 获取模板详情
  getDetail: (id: number) => 
    request.get<APIResponse<PromptTemplate>>(`/api/template/${id}`),
  
  // 使用模板（复制到我的 Prompt）
  use: (id: number) => 
    request.post<APIResponse<{ prompt_id: number }>>(`/api/template/${id}/use`),
  
  // 切换收藏
  toggleFavorite: (id: number) => 
    request.post<APIResponse<{ is_favorited: boolean }>>(`/api/template/${id}/favorite`),
  
  // 获取我的收藏
  getFavorites: (params?: {
    page?: number
    page_size?: number
  }) => 
    request.get<APIResponse<TemplateListResponse>>('/api/template/favorites/list', { params }),
  
  // 给模板评分
  rate: (id: number, data: {
    rating: number
    comment?: string
  }) => 
    request.post<APIResponse<any>>(`/api/template/${id}/rate`, data),
  
  // 用户贡献模板
  create: (data: {
    category_id: number
    title: string
    description?: string
    content: string
    variables?: TemplateVariable[]
    tags?: string[]
    difficulty?: string
  }) => 
    request.post<APIResponse<{ template_id: number }>>('/api/template/create', data),
  
  // 获取热门模板
  getPopular: (limit?: number) => 
    request.get<APIResponse<Array<{
      id: number
      title: string
      use_count: number
      rating: number
    }>>>('/api/template/stats/popular', { params: { limit } })
}

// 系统配置API
export const systemAPI = {
  // 获取全局AI配置
  getGlobalAIConfig: (): Promise<InterceptedResponse<{
    id?: number | null
    enable_default_ai: boolean
    default_ai_model: string
    default_ai_api_key: string | null
    default_ai_base_url: string
    has_api_key: boolean
    name?: string
    description?: string
  }>> => 
    request.get('/api/system/global-ai-config') as any,
  
  // 更新全局AI配置
  updateGlobalAIConfig: (data: {
    enable_default_ai?: boolean
    default_ai_model?: string
    default_ai_api_key?: string
    default_ai_base_url?: string
  }): Promise<InterceptedResponse<any>> => 
    request.put('/api/system/global-ai-config', data) as any,
  
  // 测试全局AI配置
  testGlobalAIConfig: (): Promise<InterceptedResponse<{
    model: string
    base_url: string
    response: string
  }>> => 
    request.post('/api/system/global-ai-config/test') as any
}

// 文件管理 API
export interface UploadedFileItem {
  id: number
  filename: string
  file_type: string
  file_size: number
  uploaded_at: string
  mime_type: string
}

export const fileAPI = {
  // 获取文件列表
  getList: (): Promise<InterceptedResponse<UploadedFileItem[]>> =>
    request.get('/api/files/list') as any,
  
  // 删除文件
  delete: (fileId: number): Promise<InterceptedResponse<any>> =>
    request.delete(`/api/files/${fileId}`) as any
}

// 使用统计 API
export interface DailyStats {
  date: string
  calls: number
  tokens: number
  cost: number
  avg_response_time: number
}

export interface TopPrompt {
  prompt_id: number
  title: string
  use_count: number
  total_tokens: number
  total_cost: number
  avg_response_time: number
}

export interface ModelUsage {
  model: string
  calls: number
  tokens: number
  cost: number
  avg_response_time: number
}

// Prompt 评论 API
export interface CommentUser {
  id: number
  username: string
  avatar_url?: string
}

export interface PromptComment {
  id: number
  prompt_id: number
  user_id: number
  content: string
  mentioned_user_ids?: number[]
  version?: number
  parent_id?: number
  comment_type: 'comment' | 'review' | 'suggestion'
  review_status?: 'pending' | 'approved' | 'rejected'
  is_edited: boolean
  created_at: string
  updated_at?: string
  username?: string
  avatar_url?: string
  mentioned_users?: CommentUser[]
  replies?: PromptComment[]
  reply_count: number
}

export interface CommentStats {
  total: number
  comments: number
  reviews: number
  suggestions: number
  pending_reviews: number
  approved_reviews: number
  rejected_reviews: number
}

export const commentAPI = {
  // 获取评论列表
  getComments: (promptId: number, params?: { version?: number; comment_type?: string }) =>
    request.get<APIResponse<PromptComment[]>>(`/api/prompt/${promptId}/comments`, { params }),
  
  // 创建评论
  createComment: (promptId: number, data: {
    content: string
    mentioned_user_ids?: number[]
    version?: number
    parent_id?: number
    comment_type?: string
    review_status?: string
  }) => request.post<APIResponse<PromptComment>>(`/api/prompt/${promptId}/comments`, data),
  
  // 更新评论
  updateComment: (commentId: number, data: {
    content?: string
    review_status?: string
  }) => request.put<APIResponse<PromptComment>>(`/api/prompt/comments/${commentId}`, data),
  
  // 删除评论
  deleteComment: (commentId: number) =>
    request.delete<APIResponse<null>>(`/api/prompt/comments/${commentId}`),
  
  // 获取评论统计
  getStats: (promptId: number) =>
    request.get<APIResponse<CommentStats>>(`/api/prompt/${promptId}/comments/stats`),
  
  // 搜索用户（用于@提及）
  searchUsers: (keyword: string, promptId?: number, limit?: number) =>
    request.get<APIResponse<CommentUser[]>>('/api/prompt/users/search', { 
      params: { keyword, prompt_id: promptId, limit } 
    })
}

export const statisticsAPI = {
  // 获取统计概览
  getOverview: (days?: number) =>
    request.get<APIResponse<{
      total_calls: number
      total_tokens: number
      total_input_tokens: number
      total_output_tokens: number
      total_cost: number
      avg_response_time: number
      days: number
    }>>('/api/statistics/overview', { params: { days } }),
  
  // 获取每日统计
  getDaily: (days?: number) =>
    request.get<APIResponse<DailyStats[]>>('/api/statistics/daily', { params: { days } }),
  
  // 获取最常用的 Prompt
  getTopPrompts: (params?: { limit?: number; days?: number }) =>
    request.get<APIResponse<TopPrompt[]>>('/api/statistics/top-prompts', { params }),
  
  // 获取模型使用统计
  getModelUsage: (days?: number) =>
    request.get<APIResponse<ModelUsage[]>>('/api/statistics/model-usage', { params: { days } }),
  
  // 获取每小时统计
  getHourly: (days?: number) =>
    request.get<APIResponse<{ hours: number[]; calls: number[] }>>('/api/statistics/hourly', { params: { days } })
}

// 团队工作区 API
export interface TeamInfo {
  id: number
  name: string
  description?: string
  avatar_url?: string
  owner_id: number
  is_public: boolean
  allow_member_invite: boolean
  member_count: number
  prompt_count: number
  my_role?: string
  created_at: string
  updated_at: string
}

export interface TeamMember {
  id: number
  team_id: number
  user_id: number
  username: string
  email: string
  avatar_url?: string
  role: string
  status: string
  joined_at?: string
  invited_by_username?: string
}

export interface TeamPromptItem {
  id: number
  team_id: number
  prompt_id: number
  prompt_title: string
  prompt_description?: string
  permission: string
  shared_by_username: string
  created_at: string
}

export const teamAPI = {
  // 获取我的团队列表
  getMyTeams: () =>
    request.get<APIResponse<TeamInfo[]>>('/api/team/list'),
  
  // 创建团队
  createTeam: (data: {
    name: string
    description?: string
    avatar_url?: string
    is_public?: boolean
    allow_member_invite?: boolean
  }) => request.post<APIResponse<{ id: number; name: string }>>('/api/team', data),
  
  // 获取团队详情
  getTeam: (teamId: number) =>
    request.get<APIResponse<TeamInfo>>(`/api/team/${teamId}`),
  
  // 更新团队
  updateTeam: (teamId: number, data: {
    name?: string
    description?: string
    avatar_url?: string
    is_public?: boolean
    allow_member_invite?: boolean
  }) => request.put<APIResponse<null>>(`/api/team/${teamId}`, data),
  
  // 删除团队
  deleteTeam: (teamId: number) =>
    request.delete<APIResponse<null>>(`/api/team/${teamId}`),
  
  // 获取团队成员
  getMembers: (teamId: number) =>
    request.get<APIResponse<TeamMember[]>>(`/api/team/${teamId}/members`),
  
  // 添加成员
  addMember: (teamId: number, data: {
    user_id?: number
    email?: string
    role?: string
  }) => request.post<APIResponse<null>>(`/api/team/${teamId}/members`, data),
  
  // 更新成员角色
  updateMember: (teamId: number, memberId: number, data: { role: string }) =>
    request.put<APIResponse<null>>(`/api/team/${teamId}/members/${memberId}`, data),
  
  // 移除成员
  removeMember: (teamId: number, memberId: number) =>
    request.delete<APIResponse<null>>(`/api/team/${teamId}/members/${memberId}`),
  
  // 获取团队 Prompt
  getTeamPrompts: (teamId: number, params?: { skip?: number; limit?: number }) =>
    request.get<APIResponse<{ items: TeamPromptItem[]; total: number }>>(`/api/team/${teamId}/prompts`, { params }),
  
  // 共享 Prompt 到团队
  sharePrompt: (teamId: number, data: { prompt_id: number; permission?: string }) =>
    request.post<APIResponse<null>>(`/api/team/${teamId}/prompts`, data),
  
  // 从团队移除 Prompt
  removePrompt: (teamId: number, teamPromptId: number) =>
    request.delete<APIResponse<null>>(`/api/team/${teamId}/prompts/${teamPromptId}`),
  
  // 创建邀请链接
  createInvite: (teamId: number, data?: {
    role?: string
    expires_hours?: number
    max_uses?: number
  }) => request.post<APIResponse<{ invite_code: string; expires_at?: string; max_uses: number }>>(`/api/team/${teamId}/invites`, data || {}),
  
  // 通过邀请码加入团队
  joinByInvite: (inviteCode: string) =>
    request.post<APIResponse<{ team_id: number; team_name: string }>>(`/api/team/join/${inviteCode}`)
}

