# AI Prompt Lab - AI Prompt 智能工作台

一个可以"调试 + 管理 + 对比 + 分享 Prompt"的智能工作台。

## 项目简介

AI Prompt Lab 是专业的 Prompt 工程工具，适用于：

- 打工人：提高 AI 使用效率
- AI 玩家：试验不同模型效果
- 开源社区：贡献和分享提示词库

它不是 ChatGPT 的替代品，它是 **Prompt 的 IDE + 知识库 + 运营工具**。

## 核心功能

### 1. Prompt 编辑器
- 支持变量插入（`{{变量名}}` 语法）
- Markdown 语法高亮
- 实时调用模型接口返回结果
- 版本管理和历史回溯

### 2. Prompt 管理库
- CRUD 完整功能
- 标签分类和搜索
- 收藏功能
- 版本历史管理

### 3. A/B 测试
- 同一问题调用多个 Prompt
- 对比显示响应时间
- Token 消耗统计
- 模型输出质量对比

### 4. Prompt 模板库
- 20+ 精选优质模板
- 多维度分类和筛选
- 一键使用模板到编辑器
- 收藏和评分功能
- 难度分级（入门/中级/高级）

### 5. AI 配置管理
- **多 AI 配置支持**：同时管理多个 AI 服务（OpenAI、DeepSeek、Kimi 等）
- **全局 AI 配置**：管理员可配置全局默认 AI，供所有用户使用
- **个人 AI 配置**：用户可添加自己的 AI 配置
- **配置优先级**：默认配置 > 个人配置 > 全局配置 > 环境变量
- **API Key 加密存储**：安全保存敏感信息
- **连接测试**：配置前可测试连接是否正常

### 6. 用户系统
- 注册登录（JWT 认证）
- 角色权限管理（管理员/普通用户）
- 使用频率限制
- 审计日志记录

## 技术栈

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **TypeScript** - 类型安全
- **Element Plus** - UI 组件库
- **TailwindCSS** - 原子化 CSS
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 请求
- **Marked** - Markdown 渲染
- **Highlight.js** - 代码高亮

### 后端
- **FastAPI** - 现代化 Python Web 框架
- **SQLModel** - SQL 数据库的 Python ORM
- **MySQL** - 关系型数据库
- **PyMySQL** - MySQL 驱动
- **PyJWT** - JWT 认证
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器

## 项目结构

```
ai-prompt-lab/
├─ frontend/                 # Vue3 前端
│  ├─ src/
│  │  ├─ pages/             # 页面组件
│  │  │  ├─ Login.vue
│  │  │  ├─ PromptList.vue
│  │  │  ├─ PromptEditor.vue
│  │  │  ├─ CompareTest.vue
│  │  │  ├─ Templates.vue
│  │  │  ├─ Settings.vue   # 设置页面
│  │  │  └─ admin/         # 管理员页面
│  │  │     ├─ GlobalAIConfig.vue # 全局AI配置
│  │  │     ├─ Users.vue
│  │  │     ├─ AuditLogs.vue
│  │  │     └─ SecurityConfig.vue
│  │  ├─ components/        # 公共组件
│  │  │  ├─ Layout/
│  │  │  │  ├─ Header.vue
│  │  │  │  └─ Sidebar.vue
│  │  │  ├─ PromptCard.vue
│  │  │  ├─ VariableInput.vue
│  │  │  └─ ResultViewer.vue
│  │  ├─ store/            # Pinia 状态管理
│  │  │  ├─ user.ts
│  │  │  ├─ prompt.ts
│  │  │  └─ config.ts      # AI配置状态
│  │  ├─ api/              # API 封装
│  │  ├─ router/           # 路由配置
│  │  └─ utils/            # 工具函数
│  ├─ package.json
│  ├─ vite.config.ts
│  └─ tsconfig.json
│
├─ backend/                 # FastAPI 后端
│  ├─ app/
│  │  ├─ api/              # API 路由
│  │  │  ├─ auth.py        # 认证
│  │  │  ├─ prompt.py      # Prompt 管理
│  │  │  ├─ run.py         # Prompt 执行
│  │  │  ├─ abtest.py      # A/B 测试
│  │  │  ├─ batch_test.py  # 批量测试
│  │  │  ├─ ai_config.py   # AI 配置
│  │  │  ├─ system_config.py # 全局配置
│  │  │  ├─ template.py    # 模板管理
│  │  │  └─ admin.py       # 管理功能
│  │  ├─ core/             # 核心配置
│  │  │  ├─ config.py
│  │  │  ├─ database.py
│  │  │  ├─ security.py
│  │  │  └─ deps.py
│  │  ├─ models/           # 数据模型
│  │  │  ├─ user.py
│  │  │  ├─ prompt.py
│  │  │  ├─ prompt_version.py
│  │  │  ├─ ai_config.py   # AI 配置模型
│  │  │  ├─ template.py
│  │  │  └─ abtest.py
│  │  ├─ services/         # 业务服务
│  │  │  ├─ openai_service.py # AI 调用服务
│  │  │  ├─ encryption_service.py # 加密服务
│  │  │  ├─ rate_limit.py
│  │  │  └─ audit_service.py # 审计日志
│  │  ├─ utils/            # 工具类
│  │  └─ main.py           # 应用入口
│  ├─ init_db.py           # 数据库初始化
│  ├─ migrations/          # 数据库迁移脚本
│  └─ requirements.txt     # Python 依赖
│
├─ logs/                    # 开发日志
├─ .gitignore
└─ README.md
```

## 快速开始

### 环境要求

- Node.js >= 16
- Python >= 3.10
- MySQL >= 5.7

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai-prompt-lab
```

### 2. 配置数据库

在 MySQL 中创建数据库：

```sql
CREATE DATABASE ai_prompt_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 后端配置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制 .env.example 为 .env 并修改配置
copy .env.example .env

# 初始化数据库
python init_db.py

# 启动后端服务
uvicorn app.main:app --reload --port 8000
```

后端服务将运行在 http://localhost:8000

API 文档：http://localhost:8000/docs

### 4. 前端配置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将运行在 http://localhost:5173

### 5. 访问应用

打开浏览器访问 http://localhost:5173

默认没有用户，需要先注册账号。

## 开发说明

### API 响应格式

所有 API 统一返回格式：

```json
{
  "code": 0,
  "data": { ... },
  "message": "success"
}
```

- `code`: 0 表示成功，其他值表示错误
- `data`: 响应数据
- `message`: 响应消息

### Prompt 变量语法

在 Prompt 中使用 `{{变量名}}` 来定义变量：

```
你是一个{{角色}}，请帮我{{任务}}。
```

系统会自动识别变量并提供输入界面。

### AI 配置说明

系统支持多种 AI 配置方式：

#### 1. 全局 AI 配置（推荐）
管理员可以在"管理全局配置"页面配置默认 AI，供所有用户使用：
- 访问：设置 → 管理全局配置（仅管理员可见）
- 优点：用户无需配置即可使用系统
- 支持测试连接功能

#### 2. 个人 AI 配置
用户可以在"设置"页面添加自己的 AI 配置：
- 支持多个配置同时存在
- 可以设置默认配置
- 适合使用不同 AI 服务的场景

#### 3. 环境变量配置
在 `.env` 文件中配置（用于开发和部署）：
```bash
ENABLE_DEFAULT_AI=true
DEFAULT_AI_API_KEY=sk-your-api-key
DEFAULT_AI_BASE_URL=https://api.openai.com/v1
DEFAULT_AI_MODEL=gpt-3.5-turbo
```

#### 配置优先级
```
用户默认配置 > 用户任意配置 > 全局配置 > 环境变量配置
```

## 功能特性

### 已实现

**核心功能**
- ✅ 用户注册登录（JWT 认证）
- ✅ Prompt CRUD 管理
- ✅ 变量系统（`{{变量名}}` 语法）
- ✅ Prompt 执行和结果展示
- ✅ Markdown 渲染
- ✅ 版本管理和历史回溯
- ✅ 收藏功能
- ✅ 标签分类和搜索

**AI 配置**
- ✅ 多 AI 配置管理
- ✅ 全局 AI 配置（管理员功能）
- ✅ 个人 AI 配置
- ✅ API Key 加密存储
- ✅ 连接测试功能
- ✅ 真实 AI API 集成（OpenAI、DeepSeek、Kimi 等兼容 API）

**测试与分析**
- ✅ A/B 测试对比
- ✅ 批量测试
- ✅ 频率限制
- ✅ Token 统计
- ✅ 成本估算
- ✅ 执行历史记录

**模板与安全**
- ✅ Prompt 模板库（20+精选模板）
- ✅ 模板分类和评分
- ✅ 敏感词过滤
- ✅ 审计日志
- ✅ 角色权限管理

### 计划中

- ⏳ AI 自动质量评分
- ⏳ 团队协作功能
- ⏳ Prompt 导入导出
- ⏳ 使用统计分析
- ⏳ 深色模式
- ⏳ 更多 AI 服务支持
- ⏳ Prompt 市场（分享与售卖）

## 部署

### Docker 部署（推荐）

```bash
# TODO: 添加 Docker 配置
```

### 手动部署

1. 构建前端：

```bash
cd frontend
npm run build
```

2. 配置 Nginx 反向代理

3. 使用 Gunicorn 运行后端：

```bash
cd backend
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 常见问题

### Q: 如何配置 AI 服务？

**A:** 有三种方式：

1. **全局配置（推荐）**：管理员登录后，访问"设置" → "管理全局配置"，配置后所有用户都可使用
2. **个人配置**：每个用户在"设置"页面添加自己的 AI 配置
3. **环境变量**：在 `.env` 文件中配置默认 AI

### Q: 支持哪些 AI 服务？

**A:** 支持所有兼容 OpenAI API 格式的服务：
- OpenAI (GPT-3.5, GPT-4)
- DeepSeek
- Kimi (Moonshot)
- Azure OpenAI
- 其他兼容服务

只需配置对应的 Base URL 和 API Key 即可。

### Q: API Key 安全吗？

**A:** 是的，系统采用加密存储：
- 所有 API Key 在数据库中加密保存
- 使用时自动解密
- 管理员也无法看到完整的 API Key（仅显示脱敏后的部分）

### Q: 普通用户可以看到全局 AI 配置吗？

**A:** 
- 普通用户可以**使用**全局配置，但看不到具体的 API Key
- 只有管理员可以查看和修改全局配置
- 全局配置会在 AI 配置列表中显示为 "[全局]" 标识

### Q: 如何调整频率限制？

**A:** 修改 `backend/app/services/rate_limit.py` 中的限制参数。

### Q: 数据库连接失败？

**A:** 检查 MySQL 服务是否启动，`.env` 文件中的数据库配置是否正确。

### Q: 测试连接失败怎么办？

**A:** 请检查：
1. Base URL 是否正确（注意：OpenAI 官方需要科学上网）
2. API Key 是否有效
3. 模型名称是否正确
4. 网络连接是否正常

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 开源协议

本项目采用 MIT 协议开源。

## 联系方式

如有问题或建议，欢迎提交 Issue。

---

**打造你的专属 Prompt 工作台！**

