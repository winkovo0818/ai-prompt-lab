# Prompt Git 化 - 产品规格与实现方案

## 一、愿景

将 AI Prompt Lab 打造成 **Prompt 的 GitHub**。

借鉴 Git 的版本控制思想，让团队可以：
- 分支实验不同写法
- 提交变更并 review
- 合并到主分支
- 完整追溯历史

---

## 二、核心概念映射

| Git 概念 | Prompt Git 对应 |
|----------|----------------|
| Repository | Prompt 仓库（一个 Prompt = 一个仓库） |
| Branch | 分支（实验分支、特性分支） |
| Commit | 版本（每次保存 = 一个提交） |
| Diff | 版本对比（高亮显示变更） |
| Pull Request | PR（提交分支合并请求） |
| Merge | 合并（将变更合并到目标分支） |

---

## 三、功能优先级

### P0 - 核心骨架

1. **数据库模型** - branch、commit、pull_request 三张表
2. **分支管理 API** - 创建分支、切换分支、删除分支
3. **版本控制 API** - 创建提交、获取历史、回滚
4. **前端基础** - 仓库主页、分支选择器

### P1 - 版本控制核心

5. **Diff 视图** - 计算并展示两版本差异
6. **PR 流程** - 创建、查看、合并 Pull Request
7. **前端 PR 界面** - PR 列表、详情、合并按钮

### P2 - 协作增强

8. **Review 评论** - PR 下评论讨论
9. **自动化测试配置** - PR 配置测试用例
10. **权限控制** - merge 权限、PR 创建权限

### P3 - 高级功能

11. **Pipeline 状态** - 执行结果反馈到 PR
12. **自动评分** - 执行结果自动打分影响合并

---

## 四、数据库设计

### 4.1 表结构

```sql
-- Prompt 仓库（扩展）
ALTER TABLE prompt ADD COLUMN default_branch_id INT DEFAULT NULL;

-- 分支表
CREATE TABLE prompt_branch (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prompt_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,           -- main, feature-xxx
    description TEXT,
    base_branch_id INT DEFAULT NULL,       -- 基准分支
    is_default BOOLEAN DEFAULT FALSE,
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompt(id) ON DELETE CASCADE,
    FOREIGN KEY (base_branch_id) REFERENCES prompt_branch(id),
    FOREIGN KEY (created_by) REFERENCES user(id),
    UNIQUE KEY uk_prompt_branch (prompt_id, name)
);

-- 提交记录表
CREATE TABLE prompt_commit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NOT NULL,
    parent_id INT DEFAULT NULL,            -- 上一个提交
    title VARCHAR(255) NOT NULL,          -- commit message
    content TEXT NOT NULL,
    variables_schema JSON,
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES prompt_branch(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES prompt_commit(id),
    FOREIGN KEY (created_by) REFERENCES user(id),
    INDEX idx_branch_created (branch_id, created_at DESC)
);

-- Pull Request 表
CREATE TABLE prompt_pull_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prompt_id INT NOT NULL,
    source_branch_id INT NOT NULL,
    target_branch_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('open', 'merged', 'closed') DEFAULT 'open',
    author_id INT NOT NULL,
    reviewer_id INT DEFAULT NULL,
    merged_by INT DEFAULT NULL,
    merged_at DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompt(id) ON DELETE CASCADE,
    FOREIGN KEY (source_branch_id) REFERENCES prompt_branch(id),
    FOREIGN KEY (target_branch_id) REFERENCES prompt_branch(id),
    FOREIGN KEY (author_id) REFERENCES user(id),
    FOREIGN KEY (reviewer_id) REFERENCES user(id),
    FOREIGN KEY (merged_by) REFERENCES user(id)
);
```

### 4.2 索引

```sql
CREATE INDEX idx_branch_prompt ON prompt_branch(prompt_id, is_default);
CREATE INDEX idx_commit_branch_time ON prompt_commit(branch_id, created_at DESC);
CREATE INDEX idx_pr_prompt_status ON prompt_pull_request(prompt_id, status);
```

---

## 五、API 设计

### 5.1 分支管理

**创建分支**
```
POST /api/prompt/{prompt_id}/branches
{
    "name": "feature-new-prompt",
    "description": "测试新的写法",
    "base_branch_id": 1  // 可选
}
```

**分支列表**
```
GET /api/prompt/{prompt_id}/branches
```

**切换分支**
```
PATCH /api/prompt/{prompt_id}/branches/{branch_id}/switch
```

### 5.2 版本控制

**创建提交**
```
POST /api/prompt/{prompt_id}/commits
{
    "branch_id": 2,
    "title": "优化了角色描述",
    "content": "完整内容...",
    "variables_schema": {"source_lang": "string"}
}
```

**版本历史**
```
GET /api/prompt/{prompt_id}/branches/{branch_id}/commits
```

**获取特定版本**
```
GET /api/prompt/{prompt_id}/commits/{commit_id}
```

**回滚**
```
POST /api/prompt/{prompt_id}/branches/{branch_id}/revert
{"commit_id": 99}
```

### 5.3 Diff 对比

```
GET /api/prompt/{prompt_id}/diff?from_commit=99&to_commit=101
{
    "from": {...},
    "to": {...},
    "diff": {
        "additions": 12,
        "deletions": 3,
        "segments": [
            {"type": "unchanged", "lines": [...]},
            {"type": "deleted", "lines": [...]},
            {"type": "added", "lines": [...]}
        ]
    }
}
```

### 5.4 Pull Request

**创建 PR**
```
POST /api/prompt/{prompt_id}/pull-requests
{
    "source_branch_id": 2,
    "target_branch_id": 1,
    "title": "合并：优化角色描述",
    "description": "..."
}
```

**PR 详情**
```
GET /api/prompt/{prompt_id}/pull-requests/{pr_id}
```

**合并 PR**
```
POST /api/prompt/{prompt_id}/pull-requests/{pr_id}/merge
{"merge_method": "squash"}
```

---

## 六、核心服务

### 6.1 DiffService

```python
class DiffService:
    def compute_diff(self, old_content: str, new_content: str) -> dict:
        """计算两版本差异"""
        # 使用 difflib 计算行级别差异
        # 返回: {additions, deletions, segments}
```

### 6.2 VersionControlService

```python
class VersionControlService:
    def create_branch(...) -> PromptBranch
    def create_commit(...) -> PromptCommit
    def get_branch_content(...) -> str
    def revert_to_commit(...) -> PromptCommit
```

### 6.3 PullRequestService

```python
class PullRequestService:
    def create_pr(...) -> PromptPullRequest
    def can_merge(...) -> dict
    def merge(...) -> dict
```

---

## 七、前端组件

| 组件 | 说明 |
|------|------|
| `PromptRepo.vue` | 仓库主页，显示分支、PR 列表 |
| `BranchManager.vue` | 分支选择/创建 |
| `CommitHistory.vue` | 版本历史时间线 |
| `PromptDiff.vue` | Diff 展示（绿增红删） |
| `PullRequestList.vue` | PR 列表 |
| `PullRequestDetail.vue` | PR 详情、合并按钮 |

---

## 八、现有代码影响

| 文件 | 影响 |
|------|------|
| `api/prompt.py` | 增加分支路由 |
| `models/prompt.py` | 增加 default_branch_id |
| `services/run_service.py` | 使用当前分支内容执行 |
| `services/batch_test.py` | 同上 |
| `PromptEditor.vue` | 增加提交按钮、历史入口 |
| `api/prompt.ts` | 增加分支/PR API |

---

## 九、执行顺序

```
Step 1: 数据库模型 + 分支 API（后端）
Step 2: 版本历史 + Commit API（后端）
Step 3: Diff 计算服务（后端）
Step 4: 前端仓库主页 + 分支管理
Step 5: 前端 Diff 视图 + 版本对比
Step 6: PR 流程 + 合并功能
Step 7: Review 评论 + 自动化测试
Step 8: Pipeline 集成
```