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
  user_id: number
  title: string
  content: string
  description?: string
  tags?: string[]
  is_favorite: boolean
  is_public: boolean
  version: number
  created_at: string
  updated_at: string
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
    request.put<APIResponse<UserInfo>>('/api/auth/profile', data)
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
    request.delete<APIResponse>(`/api/admin/templates/${templateId}`)
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

