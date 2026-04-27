# Prompt 测试集 MVP 方案

## 目标

先实现 3 个核心能力：

1. 给每个 `Prompt` 绑定可复用测试集
2. 保存新版本后自动跑一轮轻量测试集
3. 支持手动跑完整测试集，并和基线版本对比

## 设计原则

- 尽量复用现有 `Prompt.version`、`PromptVersion`、`batch_test` 能力
- 先做可回归、可对比、可落库的 MVP，不先做复杂评测平台
- AI 评分只做辅助，不作为唯一通过条件
- 自动触发只发生在“保存新版本后”，不在编辑过程中频繁触发

## 当前代码现状

现有基础：

- `backend/app/models/prompt.py` 已有 `Prompt.version`
- `backend/app/models/prompt_version.py` 已有版本历史表 `PromptVersion`
- `backend/app/api/batch_test.py` 已支持“一个 prompt 跑多条 case”
- `backend/app/api/abtest.py` 已支持“多个 prompt 做横向对比”
- `frontend/src/pages/CompareTest.vue` 已有测试结果页雏形

当前缺口：

- `batch_test` 接收了 `expected_output`，但没有真正做通过/失败判定
- 缺少“可复用测试集”实体，当前更像一次性批量执行记录
- 前端已有 `batchTestAPI`，但没有对应测试集管理页面
- 当前 `abtest` 适合展示对比，不适合严谨回归基准

## MVP 范围

第一版只做：

1. `smoke` / `full` 两类测试集
2. JSON 存储测试用例
3. 4 类基础断言：
   - `required_keywords`
   - `forbidden_keywords`
   - `min_quality_score`
   - `max_response_time`
4. 保存后自动跑 `smoke` 测试集
5. 编辑器右侧增加 `测试` Tab

## 数据模型

新增文件：`backend/app/models/test_suite.py`

### `PromptTestSuite`

- `id`
- `user_id`
- `prompt_id`
- `name`
- `description`
- `suite_type`: `smoke | full`
- `is_active`
- `auto_run_on_save`
- `baseline_mode`: `previous_version | fixed_version`
- `fixed_baseline_version`: 可空
- `test_cases`: JSON
- `created_at`
- `updated_at`

### `PromptTestRun`

- `id`
- `suite_id`
- `user_id`
- `prompt_id`
- `candidate_version`
- `baseline_version`
- `trigger_source`: `manual | save`
- `status`: `pending | running | completed | failed`
- `summary`: JSON
- `results`: JSON
- `created_at`
- `completed_at`

## 测试用例结构

`test_cases` 先使用 JSON 数组，示例：

```json
[
  {
    "name": "商品标题生成-基础场景",
    "variables": {
      "product_name": "iPhone 15",
      "audience": "大学生"
    },
    "expected_output": "可选，先保留",
    "required_keywords": ["iPhone 15", "大学生"],
    "forbidden_keywords": ["无法回答", "抱歉"],
    "min_quality_score": 7.5,
    "max_response_time": 8
  }
]
```

## 判定逻辑

每条 case 先计算：

- `passed`
- `assertion_results`
- `candidate_output`
- `baseline_output`
- `candidate_score`
- `baseline_score`
- `response_time`
- `error`

整轮运行汇总：

- `total_cases`
- `passed_cases`
- `failed_cases`
- `pass_rate`
- `avg_quality_score`
- `avg_response_time`
- `regression_cases`

判定策略：

- 硬规则先决定是否通过
- AI 评分用于补充参考
- 回归对比看候选版本是否明显退化

## 版本对比策略

MVP 默认：

- `baseline_mode = previous_version`
- 即保存出 `v5` 时，默认拿 `v4` 做基线

后续可支持固定基线：

- `baseline_mode = fixed_version`
- `fixed_baseline_version = 3`

## 运行方式

严谨回归采用“同 case、独立执行、再比较”的方式：

1. 候选版本对同一批 case 各执行一次
2. 基线版本对同一批 case 各执行一次
3. 对比：
   - `pass_rate`
   - 平均 AI 评分
   - 平均耗时
   - 平均 token
   - 平均 cost
   - 单 case 退化列表

不使用 `abtest.py` 当前的“多 prompt 合并一次调用”作为回归基准，因为不同 prompt 会互相干扰。

## 自动触发策略

推荐策略：

1. 编辑中不自动跑
2. 保存新版本后自动跑 `smoke`
3. 手动按钮可跑 `full`
4. 后续再扩展发布前强制回归和定时回归

触发条件：

- `Prompt` 内容发生变化
- 成功创建了新版本
- 当前 prompt 存在启用中的 `smoke` 测试集
- `auto_run_on_save = true`

## 后端实现方案

### 新增模型和迁移

- `backend/app/models/test_suite.py`
- `backend/migrations/versions/*_add_test_suite_tables.py`

### 新增服务

- `backend/app/services/test_runner_service.py`

职责：

- 按版本读取候选/基线 prompt 内容
- 执行单条 case
- 执行整套 suite
- 计算断言结果
- 汇总 summary

### 新增 API

新增文件：`backend/app/api/test_suite.py`

建议接口：

1. `GET /api/test-suite/prompt/{prompt_id}`
2. `POST /api/test-suite`
3. `PUT /api/test-suite/{suite_id}`
4. `POST /api/test-suite/{suite_id}/run`
5. `GET /api/test-suite/runs/{run_id}`
6. `GET /api/test-suite/runs`

### 接入自动触发

修改文件：`backend/app/api/prompt.py`

在 `update_prompt()` 中：

- 仅在 `content_changed` 时处理
- 新版本提交成功后查找匹配的 `smoke` 测试集
- 使用后台任务创建 `PromptTestRun`

MVP 建议先用 FastAPI `BackgroundTasks`，先不引入 Celery。

## 前端实现方案

### API 层

修改文件：`frontend/src/api/index.ts`

新增：

- `testSuiteAPI.getByPrompt(promptId)`
- `testSuiteAPI.create(data)`
- `testSuiteAPI.update(id, data)`
- `testSuiteAPI.run(id, data)`
- `testSuiteAPI.getRunDetail(runId)`
- `testSuiteAPI.getRuns(params)`

### 页面入口

优先放在：`frontend/src/pages/PromptEditor.vue`

原因：

- 用户改 prompt 时最自然的测试入口就在编辑器旁边
- 当前右侧已有 `变量`、`结果`、`分析`、`参数` Tab
- 直接新增 `测试` Tab 成本最低

### 新增组件

- `frontend/src/components/PromptTestPanel.vue`

组件职责：

1. 查看当前 prompt 的测试集
2. 编辑 `smoke` / `full` 两类测试集
3. 手动运行测试集
4. 查看最近一次运行结果

## 结果展示

MVP 结果面板先展示：

- 本次版本，例如 `v5`
- 基线版本，例如 `v4`
- 总用例数
- 通过率
- 平均 AI 评分
- 平均耗时
- 退化用例数

每条 case 展示：

- case 名称
- 输入变量
- candidate 输出
- baseline 输出
- 断言结果
- AI 评分对比
- 是否退化

## 最小门禁规则

MVP 推荐默认总规则：

- `pass_rate >= 90%`
- `regression_cases = 0`

可选增强规则：

- `avg_quality_score` 不低于基线 `0.5`

## 实施顺序

### 第 1 步

补模型和迁移：

- `backend/app/models/test_suite.py`
- `backend/migrations/versions/...`
- `backend/app/main.py`

### 第 2 步

抽测试执行服务：

- `backend/app/services/test_runner_service.py`
- 复用并收敛 `backend/app/api/batch_test.py` 中的执行逻辑

### 第 3 步

新增测试集 API：

- `backend/app/api/test_suite.py`
- `backend/app/main.py`

### 第 4 步

接入保存后自动跑：

- `backend/app/api/prompt.py`

### 第 5 步

前端接入编辑器测试面板：

- `frontend/src/api/index.ts`
- `frontend/src/components/PromptTestPanel.vue`
- `frontend/src/pages/PromptEditor.vue`

### 第 6 步

补测试：

- `backend/tests/test_test_suite.py`
  或拆到现有 `backend/tests/test_all_apis.py`

重点测试点：

- 创建测试集
- 手动运行测试集
- 保存后自动触发
- 基线版本选择
- 断言通过/失败

## 建议结论

第一版不要做“每次编辑就自动全量跑”。

更合适的工程化路径是：

1. 每次保存版本自动跑轻量 `smoke`
2. 支持手动跑完整 `full`
3. 用“硬规则 + AI 评分 + 基线对比”三层判断

这版最小、最稳，也最贴合当前仓库结构。
