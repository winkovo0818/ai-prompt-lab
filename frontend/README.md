# AI Prompt Lab - 前端

基于 Vue 3 + Vite + TypeScript + Element Plus 构建的现代化前端应用。

## 技术栈

- **Vue 3** - 组合式 API
- **Vite** - 快速的开发构建工具
- **TypeScript** - 类型安全
- **Element Plus** - UI 组件库
- **TailwindCSS** - 原子化 CSS
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端
- **Marked** - Markdown 解析
- **Highlight.js** - 代码高亮

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
src/
├── api/              # API 接口定义
│   ├── index.ts      # API 方法
│   └── request.ts    # Axios 配置
├── assets/           # 静态资源
├── components/       # 公共组件
│   ├── Layout/       # 布局组件
│   ├── PromptCard.vue
│   ├── VariableInput.vue
│   └── ResultViewer.vue
├── pages/            # 页面组件
│   ├── Login.vue
│   ├── PromptList.vue
│   ├── PromptEditor.vue
│   ├── CompareTest.vue
│   └── Market.vue
├── router/           # 路由配置
├── store/            # Pinia 状态管理
│   ├── user.ts
│   ├── prompt.ts
│   └── config.ts
├── utils/            # 工具函数
│   ├── token.ts
│   ├── format.ts
│   └── markdown.ts
├── App.vue           # 根组件
├── main.ts           # 应用入口
└── style.css         # 全局样式
```

## 功能模块

### 1. 用户认证

- 登录/注册
- JWT Token 管理
- 路由守卫

### 2. Prompt 管理

- 列表展示（搜索、过滤、分页）
- 创建/编辑/删除
- 收藏管理
- 标签分类

### 3. Prompt 编辑器

- Markdown 编辑
- 变量系统（`{{变量名}}`）
- 实时执行
- 结果展示
- 版本管理

### 4. A/B 测试

- 多 Prompt 对比
- 性能统计
- 结果可视化

### 5. Prompt 市场

- 浏览公开 Prompt
- 一键复制使用

## 状态管理

使用 Pinia 进行状态管理，主要包括：

- **userStore**: 用户信息和认证状态
- **promptStore**: Prompt 列表和当前编辑项
- **configStore**: 全局配置（模型选择、参数设置）

## 路由配置

```
/login           - 登录页
/prompts         - Prompt 列表
/editor/:id?     - Prompt 编辑器
/compare         - A/B 测试
/market          - Prompt 市场
```

## API 请求

所有 API 请求通过 Axios 实例统一处理：

- 自动添加 Authorization Header
- 统一错误处理
- 响应拦截器处理业务错误

## 开发规范

### 组件命名

- 页面组件：大驼峰命名，如 `PromptList.vue`
- 公共组件：大驼峰命名，如 `PromptCard.vue`

### 样式编写

- 优先使用 TailwindCSS 工具类
- 组件特定样式使用 Scoped CSS
- 全局样式定义在 `style.css`

### TypeScript

- 所有组件使用 TypeScript
- 定义清晰的接口类型
- 避免使用 `any` 类型

## 环境变量

在 `.env.development` 中配置开发环境变量：

```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=AI Prompt Lab
```

## 构建优化

- 代码分割
- 路由懒加载
- 图片优化
- Tree Shaking

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 常见问题

### Q: API 请求失败？

A: 检查后端服务是否启动，环境变量中的 API 地址是否正确。

### Q: 样式不生效？

A: 确保已安装 TailwindCSS 相关依赖，检查 `tailwind.config.js` 配置。

### Q: TypeScript 报错？

A: 运行 `npm run type-check` 检查类型错误。

