-- ==========================================
-- AI Prompt Lab 数据库初始化脚本
-- 版本: 1.3 (含 Prompt Git 功能)
-- 日期: 2026-04-24
-- 说明: 包含所有表结构、索引、初始数据
-- ==========================================

-- ==========================================
-- 1. 用户表
-- ==========================================

CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '用户 ID',
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `email` VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    `hashed_password` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `full_name` VARCHAR(100) NULL COMMENT '全名',
    `avatar_url` VARCHAR(500) NULL COMMENT '头像 URL',
    `role` VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色: admin/user',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_users_username` (`username`),
    INDEX `idx_users_email` (`email`),
    INDEX `idx_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ==========================================
-- 2. Prompt 主表
-- ==========================================

CREATE TABLE IF NOT EXISTS `prompts` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT 'Prompt ID',
    `user_id` INT NOT NULL COMMENT '所有者用户 ID',
    `title` VARCHAR(200) NOT NULL COMMENT '标题',
    `content` TEXT NOT NULL COMMENT '内容',
    `description` VARCHAR(500) NULL COMMENT '描述',
    `tags` TEXT NULL COMMENT '标签 JSON 数组',
    `is_public` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否公开',
    `version` INT NOT NULL DEFAULT 1 COMMENT '版本号',
    `default_branch_id` INT NULL COMMENT '默认分支 ID (Git 功能)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_prompts_user_id` (`user_id`),
    INDEX `idx_prompts_is_public` (`is_public`),
    INDEX `idx_prompts_updated_at` (`updated_at`),
    INDEX `idx_prompt_default_branch` (`default_branch_id`),

    CONSTRAINT `fk_prompts_user` FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt 主表';

-- ==========================================
-- 3. 用户 Prompt 收藏表
-- ==========================================

CREATE TABLE IF NOT EXISTS `user_prompt_favorites` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '收藏 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `prompt_id` INT NOT NULL COMMENT 'Prompt ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_prompt_favorite` (`user_id`, `prompt_id`),
    INDEX `idx_user_prompt_favorites_user_id` (`user_id`),
    INDEX `idx_user_prompt_favorites_prompt_id` (`prompt_id`),

    CONSTRAINT `fk_upf_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_upf_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户 Prompt 收藏表';

-- ==========================================
-- 4. Prompt 版本历史表 (旧版，保留兼容)
-- ==========================================

CREATE TABLE IF NOT EXISTS `prompt_versions` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '版本 ID',
    `prompt_id` INT NOT NULL COMMENT 'Prompt ID',
    `version` INT NOT NULL COMMENT '版本号',
    `title` VARCHAR(200) NOT NULL COMMENT '版本标题',
    `content` TEXT NOT NULL COMMENT '内容',
    `description` VARCHAR(500) NULL COMMENT '描述',
    `change_summary` VARCHAR(500) NULL COMMENT '变更摘要',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_prompt_version` (`prompt_id`, `version`),
    INDEX `idx_prompt_versions_prompt_id` (`prompt_id`),
    INDEX `idx_prompt_versions_version` (`version`),

    CONSTRAINT `fk_pv_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt 版本历史表';

-- ==========================================
-- 5. Prompt 分支表 (Git 功能)
-- ==========================================

CREATE TABLE IF NOT EXISTS `prompt_branch` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '分支 ID',
    `prompt_id` INT NOT NULL COMMENT '所属 Prompt ID',
    `name` VARCHAR(100) NOT NULL COMMENT '分支名称，如 main, feature-xxx',
    `description` TEXT NULL COMMENT '分支描述',
    `base_branch_id` INT NULL COMMENT '基准分支 ID，为 NULL 表示从零创建',
    `is_default` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否默认分支',
    `created_by` INT NOT NULL COMMENT '创建者用户 ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_branch_prompt` (`prompt_id`, `is_default`),
    UNIQUE KEY `uk_prompt_branch` (`prompt_id`, `name`),

    CONSTRAINT `fk_branch_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_branch_base` FOREIGN KEY (`base_branch_id`) REFERENCES `prompt_branch` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_branch_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt 分支表';

-- ==========================================
-- 6. Prompt 提交记录表 (Git 功能)
-- ==========================================

CREATE TABLE IF NOT EXISTS `prompt_commit` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '提交 ID',
    `branch_id` INT NOT NULL COMMENT '所属分支 ID',
    `parent_id` INT NULL COMMENT '父提交 ID，支持提交链表',
    `title` VARCHAR(255) NOT NULL COMMENT '提交信息',
    `content` TEXT NOT NULL COMMENT '提交时的完整内容',
    `variables_schema` JSON NULL COMMENT '变量定义 JSON',
    `created_by` INT NOT NULL COMMENT '创建者用户 ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    INDEX `idx_commit_branch_time` (`branch_id`, `created_at` DESC),
    INDEX `idx_commit_parent` (`parent_id`),

    CONSTRAINT `fk_commit_branch` FOREIGN KEY (`branch_id`) REFERENCES `prompt_branch` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_commit_parent` FOREIGN KEY (`parent_id`) REFERENCES `prompt_commit` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_commit_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt 提交记录表';

-- ==========================================
-- 7. Prompt Pull Request 表 (Git 功能)
-- ==========================================

CREATE TABLE IF NOT EXISTS `prompt_pull_request` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT 'PR ID',
    `prompt_id` INT NOT NULL COMMENT '所属 Prompt ID',
    `source_branch_id` INT NOT NULL COMMENT '源分支 ID',
    `target_branch_id` INT NOT NULL COMMENT '目标分支 ID',
    `title` VARCHAR(255) NOT NULL COMMENT 'PR 标题',
    `description` TEXT NULL COMMENT 'PR 描述',
    `status` ENUM('open', 'merged', 'closed') NOT NULL DEFAULT 'open' COMMENT 'PR 状态',
    `author_id` INT NOT NULL COMMENT '作者用户 ID',
    `reviewer_id` INT NULL COMMENT '审核人用户 ID',
    `merged_by` INT NULL COMMENT '合并人用户 ID',
    `merged_at` DATETIME NULL COMMENT '合并时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_pr_prompt_status` (`prompt_id`, `status`),
    INDEX `idx_pr_author` (`author_id`),
    INDEX `idx_pr_source` (`source_branch_id`),
    INDEX `idx_pr_target` (`target_branch_id`),

    CONSTRAINT `fk_pr_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pr_source` FOREIGN KEY (`source_branch_id`) REFERENCES `prompt_branch` (`id`),
    CONSTRAINT `fk_pr_target` FOREIGN KEY (`target_branch_id`) REFERENCES `prompt_branch` (`id`),
    CONSTRAINT `fk_pr_author` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
    CONSTRAINT `fk_pr_reviewer` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`id`),
    CONSTRAINT `fk_pr_merger` FOREIGN KEY (`merged_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt Pull Request 表';

-- ==========================================
-- 8. AI 配置表
-- ==========================================

CREATE TABLE IF NOT EXISTS `ai_configs` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '配置 ID',
    `user_id` INT NULL COMMENT '用户 ID，NULL 表示全局配置',
    `name` VARCHAR(100) NOT NULL COMMENT '配置名称',
    `base_url` VARCHAR(500) NOT NULL COMMENT 'API 地址',
    `api_key` VARCHAR(500) NOT NULL COMMENT '加密后的 API Key',
    `model` VARCHAR(100) NOT NULL COMMENT '模型名称',
    `description` VARCHAR(500) NULL COMMENT '描述',
    `is_default` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否默认',
    `is_global` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否全局配置',
    `priority` INT NOT NULL DEFAULT 0 COMMENT '优先级',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_ai_configs_user_id` (`user_id`),
    INDEX `idx_ai_configs_is_default` (`is_default`),
    INDEX `idx_ai_configs_is_global` (`is_global`),

    CONSTRAINT `fk_ai_config_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI 配置表';

-- ==========================================
-- 9. A/B 测试结果表
-- ==========================================

CREATE TABLE IF NOT EXISTS `abtest_results` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '测试 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `test_name` VARCHAR(200) NOT NULL COMMENT '测试名称',
    `input_variables` JSON NULL COMMENT '输入变量 JSON',
    `prompt_ids` JSON NOT NULL COMMENT '参与测试的 Prompt ID 列表',
    `results` JSON NOT NULL COMMENT '测试结果 JSON',
    `quality_scores` JSON NULL COMMENT '质量评分 JSON',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    INDEX `idx_abtest_results_user_id` (`user_id`),
    INDEX `idx_abtest_results_created_at` (`created_at`),

    CONSTRAINT `fk_abtest_results_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='A/B 测试结果表';

-- ==========================================
-- 10. 执行历史表
-- ==========================================

CREATE TABLE IF NOT EXISTS `execution_history` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '记录 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `prompt_id` INT NULL COMMENT 'Prompt ID',
    `prompt_content` TEXT NOT NULL COMMENT '执行时的 Prompt 内容',
    `prompt_version` INT NOT NULL DEFAULT 1 COMMENT '执行时的 Prompt 版本',
    `variables` JSON NULL COMMENT '变量值 JSON',
    `final_prompt` TEXT NOT NULL COMMENT '替换变量后的最终 Prompt',
    `model` VARCHAR(100) NOT NULL COMMENT '使用的模型',
    `temperature` REAL NOT NULL DEFAULT 0.7 COMMENT '温度参数',
    `max_tokens` INT NOT NULL DEFAULT 2000 COMMENT '最大输出 Token',
    `output` TEXT NOT NULL COMMENT 'AI 输出',
    `input_tokens` INT NOT NULL DEFAULT 0 COMMENT '输入 Token 数',
    `output_tokens` INT NOT NULL DEFAULT 0 COMMENT '输出 Token 数',
    `total_tokens` INT NOT NULL DEFAULT 0 COMMENT '总 Token 数',
    `cost` REAL NOT NULL DEFAULT 0.0 COMMENT '估算成本',
    `response_time` REAL NOT NULL DEFAULT 0.0 COMMENT '响应时间（秒）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    INDEX `idx_execution_history_user_id` (`user_id`),
    INDEX `idx_execution_history_prompt_id` (`prompt_id`),
    INDEX `idx_execution_history_created_at` (`created_at`),

    CONSTRAINT `fk_exec_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_exec_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行历史表';

-- ==========================================
-- 11. 质量评估表
-- ==========================================

CREATE TABLE IF NOT EXISTS `quality_evaluations` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '评估 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `test_type` VARCHAR(50) NOT NULL COMMENT '测试类型: abtest/batch/single',
    `test_id` INT NULL COMMENT '测试记录 ID',
    `prompt_id` INT NULL COMMENT 'Prompt ID',
    `prompt_content` TEXT NOT NULL COMMENT 'Prompt 内容',
    `output_content` TEXT NOT NULL COMMENT '输出内容',
    `accuracy_score` REAL NOT NULL DEFAULT 0.0 COMMENT '准确性评分',
    `relevance_score` REAL NOT NULL DEFAULT 0.0 COMMENT '相关性评分',
    `fluency_score` REAL NOT NULL DEFAULT 0.0 COMMENT '流畅度评分',
    `creativity_score` REAL NOT NULL DEFAULT 0.0 COMMENT '创意性评分',
    `safety_score` REAL NOT NULL DEFAULT 0.0 COMMENT '安全性评分',
    `overall_score` REAL NOT NULL DEFAULT 0.0 COMMENT '综合评分',
    `evaluation_details` JSON NULL COMMENT '详细评价 JSON',
    `safety_issues` JSON NULL COMMENT '安全问题 JSON',
    `has_sensitive_content` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否包含敏感内容',
    `response_time` REAL NOT NULL DEFAULT 0.0 COMMENT '响应时间',
    `token_count` INT NOT NULL DEFAULT 0 COMMENT 'Token 数',
    `cost` REAL NOT NULL DEFAULT 0.0 COMMENT '成本',
    `cost_efficiency_score` REAL NOT NULL DEFAULT 0.0 COMMENT '成本效益评分',
    `strengths` JSON NULL COMMENT '优点 JSON',
    `weaknesses` JSON NULL COMMENT '缺点 JSON',
    `suggestions` JSON NULL COMMENT '建议 JSON',
    `evaluation_model` VARCHAR(100) NOT NULL COMMENT '评测模型',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    INDEX `idx_quality_evaluations_user_id` (`user_id`),
    INDEX `idx_quality_evaluations_prompt_id` (`prompt_id`),
    INDEX `idx_quality_evaluations_test` (`test_type`, `test_id`),
    INDEX `idx_quality_evaluations_created_at` (`created_at`),

    CONSTRAINT `fk_qe_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_qe_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='质量评估表';

-- ==========================================
-- 12. 模板分类表
-- ==========================================

CREATE TABLE IF NOT EXISTS `template_categories` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '分类 ID',
    `name` VARCHAR(100) NOT NULL COMMENT '分类名称',
    `name_en` VARCHAR(100) NULL COMMENT '英文名称',
    `description` VARCHAR(500) NULL COMMENT '描述',
    `icon` VARCHAR(50) NOT NULL DEFAULT '📁' COMMENT '图标',
    `parent_id` INT NULL COMMENT '父分类 ID',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_template_categories_parent_id` (`parent_id`),
    INDEX `idx_template_categories_sort_order` (`sort_order`),

    CONSTRAINT `fk_tc_parent` FOREIGN KEY (`parent_id`) REFERENCES `template_categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模板分类表';

-- ==========================================
-- 13. Prompt 模板表
-- ==========================================

CREATE TABLE IF NOT EXISTS `prompt_templates` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '模板 ID',
    `category_id` INT NOT NULL COMMENT '分类 ID',
    `title` VARCHAR(200) NOT NULL COMMENT '标题',
    `description` VARCHAR(500) NULL COMMENT '描述',
    `content` TEXT NOT NULL COMMENT '模板内容',
    `variables` JSON NULL COMMENT '变量定义',
    `example_input` TEXT NULL COMMENT '示例输入',
    `example_output` TEXT NULL COMMENT '示例输出',
    `tags` TEXT NULL COMMENT '标签',
    `difficulty` VARCHAR(20) NOT NULL DEFAULT 'beginner' COMMENT '难度: beginner/intermediate/advanced',
    `use_count` INT NOT NULL DEFAULT 0 COMMENT '使用次数',
    `favorite_count` INT NOT NULL DEFAULT 0 COMMENT '收藏次数',
    `rating` REAL NOT NULL DEFAULT 0.0 COMMENT '平均评分',
    `rating_count` INT NOT NULL DEFAULT 0 COMMENT '评分次数',
    `author_id` INT NULL COMMENT '作者用户 ID',
    `is_official` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否官方',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    `is_featured` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否推荐',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_prompt_templates_category_id` (`category_id`),
    INDEX `idx_prompt_templates_difficulty` (`difficulty`),
    INDEX `idx_prompt_templates_is_featured` (`is_featured`),
    INDEX `idx_prompt_templates_use_count` (`use_count`),

    CONSTRAINT `fk_pt_category` FOREIGN KEY (`category_id`) REFERENCES `template_categories` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pt_author` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt 模板表';

-- ==========================================
-- 14. 用户模板收藏表
-- ==========================================

CREATE TABLE IF NOT EXISTS `user_template_favorites` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '收藏 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `template_id` INT NOT NULL COMMENT '模板 ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_template_favorite` (`user_id`, `template_id`),
    INDEX `idx_user_template_favorites_user_id` (`user_id`),
    INDEX `idx_user_template_favorites_template_id` (`template_id`),

    CONSTRAINT `fk_utf_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_utf_template` FOREIGN KEY (`template_id`) REFERENCES `prompt_templates` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户模板收藏表';

-- ==========================================
-- 15. 模板评分表
-- ==========================================

CREATE TABLE IF NOT EXISTS `template_ratings` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '评分 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `template_id` INT NOT NULL COMMENT '模板 ID',
    `rating` INT NOT NULL COMMENT '评分 1-5',
    `comment` TEXT NULL COMMENT '评论内容',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_template_rating` (`user_id`, `template_id`),
    INDEX `idx_template_ratings_template_id` (`template_id`),
    INDEX `idx_template_ratings_user_id` (`user_id`),

    CONSTRAINT `fk_tr_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_tr_template` FOREIGN KEY (`template_id`) REFERENCES `prompt_templates` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模板评分表';

-- ==========================================
-- 16. 敏感词表
-- ==========================================

CREATE TABLE IF NOT EXISTS `sensitive_words` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '词 ID',
    `word` VARCHAR(100) NOT NULL UNIQUE COMMENT '敏感词',
    `category` VARCHAR(50) NULL COMMENT '分类',
    `severity` VARCHAR(20) NOT NULL DEFAULT 'medium' COMMENT '严重程度: low/medium/high/critical',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_sensitive_words_word` (`word`),
    INDEX `idx_sensitive_words_category` (`category`),
    INDEX `idx_sensitive_words_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='敏感词表';

-- ==========================================
-- 17. 审计日志表
-- ==========================================

CREATE TABLE IF NOT EXISTS `audit_logs` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '日志 ID',
    `user_id` INT NULL COMMENT '用户 ID',
    `action` VARCHAR(50) NOT NULL COMMENT '操作类型',
    `resource_type` VARCHAR(50) NOT NULL COMMENT '资源类型',
    `resource_id` INT NULL COMMENT '资源 ID',
    `details` JSON NULL COMMENT '详细信息',
    `ip_address` VARCHAR(50) NULL COMMENT 'IP 地址',
    `user_agent` TEXT NULL COMMENT 'User Agent',
    `status` VARCHAR(20) NOT NULL DEFAULT 'success' COMMENT '状态: success/failure',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    INDEX `idx_audit_logs_user_id` (`user_id`),
    INDEX `idx_audit_logs_action` (`action`),
    INDEX `idx_audit_logs_resource_type` (`resource_type`),
    INDEX `idx_audit_logs_created_at` (`created_at`),

    CONSTRAINT `fk_al_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';

-- ==========================================
-- 18. 网站设置表
-- ==========================================

CREATE TABLE IF NOT EXISTS `site_settings` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '设置 ID',
    `site_name` VARCHAR(100) NOT NULL DEFAULT 'AI Prompt Lab' COMMENT '网站名称',
    `site_description` VARCHAR(500) NOT NULL DEFAULT 'AI Prompt 智能工作台' COMMENT '网站描述',
    `site_keywords` VARCHAR(200) NOT NULL DEFAULT 'AI, Prompt, 工作台' COMMENT '网站关键词',
    `page_size` INT NOT NULL DEFAULT 20 COMMENT '分页大小',
    `allow_register` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否允许注册',
    `default_public` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Prompt 默认公开',
    `enable_market` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用市场',
    `enable_abtest` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用 A/B 测试',
    `max_abtest_prompts` INT NOT NULL DEFAULT 5 COMMENT 'A/B 测试最大 Prompt 数',
    `version` VARCHAR(20) NOT NULL DEFAULT '1.0.0' COMMENT '系统版本',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='网站设置表';

-- ==========================================
-- 19. 团队表
-- ==========================================

CREATE TABLE IF NOT EXISTS `teams` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '团队 ID',
    `name` VARCHAR(100) NOT NULL COMMENT '团队名称',
    `description` VARCHAR(500) NULL COMMENT '团队描述',
    `avatar_url` VARCHAR(500) NULL COMMENT '团队头像 URL',
    `owner_id` INT NOT NULL COMMENT '所有者用户 ID',
    `is_public` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否公开团队',
    `allow_member_invite` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否允许成员邀请',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_teams_name` (`name`),
    INDEX `idx_teams_owner` (`owner_id`),

    CONSTRAINT `fk_teams_owner` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='团队表';

-- ==========================================
-- 20. 团队成员表
-- ==========================================

CREATE TABLE IF NOT EXISTS `team_members` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '成员 ID',
    `team_id` INT NOT NULL COMMENT '团队 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `role` VARCHAR(20) NOT NULL DEFAULT 'member' COMMENT '角色: owner/admin/member',
    `permission` VARCHAR(20) NOT NULL DEFAULT 'read' COMMENT '权限: read/write/admin',
    `invited_by` INT NULL COMMENT '邀请人用户 ID',
    `joined_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_team_member` (`team_id`, `user_id`),
    INDEX `idx_team_members_user_id` (`user_id`),
    INDEX `idx_team_members_role` (`role`),

    CONSTRAINT `fk_tm_team` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_tm_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_tm_invited_by` FOREIGN KEY (`invited_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='团队成员表';

-- ==========================================
-- 21. 团队 Prompt 共享表
-- ==========================================

CREATE TABLE IF NOT EXISTS `team_prompts` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `team_id` INT NOT NULL COMMENT '团队 ID',
    `prompt_id` INT NOT NULL COMMENT 'Prompt ID',
    `shared_by` INT NOT NULL COMMENT '分享人用户 ID',
    `permission` VARCHAR(20) NOT NULL DEFAULT 'view' COMMENT '权限: view/edit',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_team_prompt` (`team_id`, `prompt_id`),
    INDEX `idx_team_prompts_team_id` (`team_id`),
    INDEX `idx_team_prompts_prompt_id` (`prompt_id`),

    CONSTRAINT `fk_tp_team` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_tp_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_tp_shared_by` FOREIGN KEY (`shared_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='团队 Prompt 共享表';

-- ==========================================
-- 22. Prompt 评论表
-- ==========================================

CREATE TABLE IF NOT EXISTS `prompt_comments` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '评论 ID',
    `prompt_id` INT NOT NULL COMMENT 'Prompt ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `content` TEXT NOT NULL COMMENT '评论内容',
    `mentioned_user_ids` JSON NULL COMMENT '提及用户 ID JSON',
    `version` INT NULL COMMENT '关联版本号',
    `parent_id` INT NULL COMMENT '父评论 ID（用于回复）',
    `comment_type` VARCHAR(20) NOT NULL DEFAULT 'comment' COMMENT '评论类型',
    `review_status` VARCHAR(20) NULL COMMENT '评审状态',
    `is_edited` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已编辑',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_prompt_comments_prompt_id` (`prompt_id`),
    INDEX `idx_prompt_comments_user_id` (`user_id`),
    INDEX `idx_prompt_comments_version` (`version`),
    INDEX `idx_prompt_comments_parent_id` (`parent_id`),

    CONSTRAINT `fk_pc_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pc_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pc_parent` FOREIGN KEY (`parent_id`) REFERENCES `prompt_comments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt 评论表';

-- ==========================================
-- 23. 团队邀请表
-- ==========================================

CREATE TABLE IF NOT EXISTS `team_invites` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '邀请 ID',
    `team_id` INT NOT NULL COMMENT '团队 ID',
    `invite_code` VARCHAR(50) NOT NULL UNIQUE COMMENT '邀请码',
    `email` VARCHAR(100) NULL COMMENT '指定邀请邮箱',
    `role` VARCHAR(20) NOT NULL DEFAULT 'viewer' COMMENT '加入角色',
    `created_by` INT NOT NULL COMMENT '创建者用户 ID',
    `expires_at` DATETIME NULL COMMENT '过期时间',
    `max_uses` INT NOT NULL DEFAULT 1 COMMENT '最大使用次数',
    `used_count` INT NOT NULL DEFAULT 0 COMMENT '已使用次数',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    INDEX `idx_team_invites_team_id` (`team_id`),
    INDEX `idx_team_invites_invite_code` (`invite_code`),

    CONSTRAINT `fk_ti_team` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ti_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='团队邀请表';

-- ==========================================
-- 24. 上传文件表
-- ==========================================

CREATE TABLE IF NOT EXISTS `uploaded_files` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '文件 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `filename` VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `file_path` VARCHAR(500) NOT NULL COMMENT '服务器存储路径',
    `file_type` VARCHAR(50) NOT NULL COMMENT '文件类型',
    `mime_type` VARCHAR(100) NOT NULL COMMENT 'MIME 类型',
    `file_size` INT NOT NULL COMMENT '文件大小',
    `extracted_text` TEXT NULL COMMENT '提取文本',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否删除',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_uploaded_files_user_id` (`user_id`),
    INDEX `idx_uploaded_files_created_at` (`created_at`),

    CONSTRAINT `fk_uploaded_files_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='上传文件表';

-- ==========================================
-- 25. API 配额表
-- ==========================================

CREATE TABLE IF NOT EXISTS `api_quotas` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '配额 ID',
    `quota_type` VARCHAR(20) NOT NULL COMMENT '配额类型: user/team',
    `target_id` INT NOT NULL COMMENT '目标 ID',
    `requests_per_minute` INT NOT NULL DEFAULT 60 COMMENT '每分钟请求数',
    `requests_per_hour` INT NOT NULL DEFAULT 1000 COMMENT '每小时请求数',
    `requests_per_day` INT NOT NULL DEFAULT 10000 COMMENT '每天请求数',
    `requests_per_month` INT NOT NULL DEFAULT 100000 COMMENT '每月请求数',
    `tokens_per_day` INT NOT NULL DEFAULT 1000000 COMMENT '每日 Token 限制',
    `tokens_per_month` INT NOT NULL DEFAULT 10000000 COMMENT '每月 Token 限制',
    `cost_per_day` REAL NOT NULL DEFAULT 10.0 COMMENT '每日费用限制',
    `cost_per_month` REAL NOT NULL DEFAULT 100.0 COMMENT '每月费用限制',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `description` VARCHAR(500) NULL COMMENT '描述',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_api_quotas_quota_type` (`quota_type`),
    INDEX `idx_api_quotas_target_id` (`target_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API 配额表';

-- ==========================================
-- 26. API 使用统计表
-- ==========================================

CREATE TABLE IF NOT EXISTS `api_usage` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '使用统计 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `team_id` INT NULL COMMENT '团队 ID',
    `usage_date` DATETIME NOT NULL COMMENT '统计日期',
    `request_count` INT NOT NULL DEFAULT 0 COMMENT '请求次数',
    `total_tokens` INT NOT NULL DEFAULT 0 COMMENT '总 Token 数',
    `input_tokens` INT NOT NULL DEFAULT 0 COMMENT '输入 Token 数',
    `output_tokens` INT NOT NULL DEFAULT 0 COMMENT '输出 Token 数',
    `total_cost` REAL NOT NULL DEFAULT 0.0 COMMENT '总费用',
    `model_usage_details` TEXT NULL COMMENT '模型使用详情 JSON',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_api_usage_user_id` (`user_id`),
    INDEX `idx_api_usage_team_id` (`team_id`),
    INDEX `idx_api_usage_usage_date` (`usage_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API 使用统计表';

-- ==========================================
-- 27. Prompt 测试集表
-- ==========================================

CREATE TABLE IF NOT EXISTS `prompt_test_suites` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '测试集 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `prompt_id` INT NOT NULL COMMENT 'Prompt ID',
    `name` VARCHAR(200) NOT NULL COMMENT '测试集名称',
    `description` TEXT NULL COMMENT '描述',
    `suite_type` VARCHAR(20) NOT NULL DEFAULT 'smoke' COMMENT '测试集类型',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `auto_run_on_save` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '保存后自动运行',
    `baseline_mode` VARCHAR(50) NOT NULL DEFAULT 'previous_version' COMMENT '基线模式',
    `fixed_baseline_version` INT NULL COMMENT '固定基线版本',
    `test_cases` JSON NOT NULL COMMENT '测试用例 JSON',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_prompt_test_suites_user_id` (`user_id`),
    INDEX `idx_prompt_test_suites_prompt_id` (`prompt_id`),

    CONSTRAINT `fk_pts_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pts_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt 测试集表';

-- ==========================================
-- 28. Prompt 测试运行表
-- ==========================================

CREATE TABLE IF NOT EXISTS `prompt_test_runs` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '测试运行 ID',
    `suite_id` INT NOT NULL COMMENT '测试集 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `prompt_id` INT NOT NULL COMMENT 'Prompt ID',
    `candidate_version` INT NOT NULL COMMENT '候选版本',
    `baseline_version` INT NULL COMMENT '基线版本',
    `trigger_source` VARCHAR(50) NOT NULL DEFAULT 'manual' COMMENT '触发来源',
    `status` VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT '状态',
    `summary` JSON NOT NULL COMMENT '汇总 JSON',
    `results` JSON NOT NULL COMMENT '结果 JSON',
    `error` TEXT NULL COMMENT '错误信息',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `completed_at` DATETIME NULL COMMENT '完成时间',

    PRIMARY KEY (`id`),
    INDEX `idx_prompt_test_runs_suite_id` (`suite_id`),
    INDEX `idx_prompt_test_runs_user_id` (`user_id`),
    INDEX `idx_prompt_test_runs_prompt_id` (`prompt_id`),
    INDEX `idx_prompt_test_runs_candidate_version` (`candidate_version`),
    INDEX `idx_prompt_test_runs_baseline_version` (`baseline_version`),

    CONSTRAINT `fk_ptr_suite` FOREIGN KEY (`suite_id`) REFERENCES `prompt_test_suites` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ptr_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ptr_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt 测试运行表';

-- ==========================================
-- 29. 批量测试结果表
-- ==========================================

CREATE TABLE IF NOT EXISTS `batch_test_results` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '批量测试 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `test_name` VARCHAR(200) NOT NULL COMMENT '测试名称',
    `prompt_id` INT NOT NULL COMMENT 'Prompt ID',
    `test_cases` JSON NOT NULL COMMENT '测试用例 JSON',
    `results` JSON NOT NULL COMMENT '结果 JSON',
    `total_cases` INT NOT NULL DEFAULT 0 COMMENT '总用例数',
    `success_count` INT NOT NULL DEFAULT 0 COMMENT '成功数',
    `failure_count` INT NOT NULL DEFAULT 0 COMMENT '失败数',
    `avg_response_time` REAL NOT NULL DEFAULT 0.0 COMMENT '平均响应时间',
    `avg_token_count` INT NOT NULL DEFAULT 0 COMMENT '平均 Token 数',
    `avg_cost` REAL NOT NULL DEFAULT 0.0 COMMENT '平均成本',
    `avg_quality_score` REAL NOT NULL DEFAULT 0.0 COMMENT '平均质量分',
    `model` VARCHAR(100) NOT NULL COMMENT '模型',
    `temperature` REAL NOT NULL DEFAULT 0.7 COMMENT '温度参数',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `completed_at` DATETIME NULL COMMENT '完成时间',

    PRIMARY KEY (`id`),
    INDEX `idx_batch_test_results_user_id` (`user_id`),
    INDEX `idx_batch_test_results_prompt_id` (`prompt_id`),

    CONSTRAINT `fk_btr_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_btr_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='批量测试结果表';

-- ==========================================
-- 30. 对比分析报告表
-- ==========================================

CREATE TABLE IF NOT EXISTS `comparison_reports` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '报告 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `abtest_id` INT NOT NULL COMMENT 'A/B 测试 ID',
    `winner_prompt_id` INT NULL COMMENT '获胜 Prompt ID',
    `winner_reason` TEXT NOT NULL COMMENT '获胜原因',
    `comparison_data` JSON NOT NULL COMMENT '对比数据 JSON',
    `chart_data` JSON NOT NULL COMMENT '图表数据 JSON',
    `summary` TEXT NOT NULL COMMENT '摘要',
    `recommendations` JSON NOT NULL COMMENT '建议 JSON',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    INDEX `idx_comparison_reports_user_id` (`user_id`),
    INDEX `idx_comparison_reports_abtest_id` (`abtest_id`),

    CONSTRAINT `fk_cr_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_cr_abtest` FOREIGN KEY (`abtest_id`) REFERENCES `abtest_results` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对比分析报告表';

-- ==========================================
-- 初始数据
-- ==========================================

-- 插入默认网站设置
INSERT INTO `site_settings` (`id`, `site_name`, `site_description`, `site_keywords`)
VALUES (1, 'AI Prompt Lab', '企业级 AI 提示词管理和测试平台', 'AI, Prompt, 工作台')
ON DUPLICATE KEY UPDATE `site_name` = VALUES(`site_name`);

-- 插入默认管理员账户
-- 用户名: admin / 密码: admin123
INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `full_name`, `role`, `is_active`)
VALUES (
    1,
    'admin',
    'admin@aipromptlab.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIvAprzm3u',
    '系统管理员',
    'admin',
    1
)
ON DUPLICATE KEY UPDATE `username` = VALUES(`username`);

-- 插入默认模板分类
INSERT INTO `template_categories` (`id`, `name`, `name_en`, `description`, `icon`, `sort_order`)
VALUES
    (1, '文案创作', 'Copywriting', '各类文案、广告、营销内容创作', '✍️', 1),
    (2, '代码开发', 'Coding', '代码生成、调试、优化相关', '💻', 2),
    (3, '数据分析', 'Data Analysis', '数据处理、分析、可视化', '📊', 3),
    (4, '教育培训', 'Education', '教学、培训、学习相关', '📚', 4),
    (5, '商业分析', 'Business', '商业策略、市场分析', '💼', 5),
    (6, '创意设计', 'Creative', '创意构思、设计灵感', '🎨', 6)
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);

-- 插入示例模板
INSERT INTO `prompt_templates` (
    `id`, `category_id`, `title`, `description`, `content`,
    `difficulty`, `is_official`, `is_featured`, `use_count`
)
VALUES
    (
        1, 1, '专业文档翻译助手',
        '高质量的专业文档翻译，保持原文格式和专业术语',
        '你是一位专业的翻译专家。请将以下{{source_language}}文本翻译成{{target_language}}，要求：\n1. 保持专业术语的准确性\n2. 保持原文的格式和结构\n3. 翻译要流畅自然\n4. 必要时添加注释说明\n\n原文：\n{{text}}',
        'beginner', 1, 1, 0
    ),
    (
        2, 1, 'Slogan 创意生成器',
        '为品牌或产品创建吸引人的 Slogan',
        '你是一位资深的品牌营销专家。请为以下产品/品牌创作 5 个吸引人的 Slogan：\n\n产品/品牌名称：{{product_name}}\n目标受众：{{target_audience}}\n核心卖点：{{key_features}}\n品牌调性：{{brand_tone}}\n\n要求：\n1. 简洁有力，易于记忆\n2. 突出产品核心价值\n3. 符合目标受众喜好\n4. 体现品牌独特性',
        'beginner', 1, 1, 0
    ),
    (
        3, 2, '代码审查助手',
        '帮助发现代码中的问题和改进建议',
        '你是一位经验丰富的代码审查专家。请审查以下{{language}}代码，提供详细的反馈：\n\n代码：\n```{{language}}\n{{code}}\n```\n\n请从以下角度进行审查：\n1. 代码质量和可读性\n2. 潜在的 bug 和错误\n3. 性能优化建议\n4. 安全性问题\n5. 最佳实践建议',
        'intermediate', 1, 1, 0
    ),
    (
        4, 3, '数据分析报告生成',
        '根据数据生成专业的分析报告',
        '你是一位专业的数据分析师。请根据以下数据生成一份详细的分析报告：\n\n数据主题：{{topic}}\n数据摘要：{{data_summary}}\n分析目标：{{goals}}\n\n请包含：\n1. 数据概览\n2. 关键发现\n3. 趋势分析\n4. 洞察和建议\n5. 可视化建议',
        'intermediate', 1, 1, 0
    ),
    (
        5, 4, '个性化学习计划',
        '为学习者制定个性化的学习路径',
        '你是一位经验丰富的教育顾问。请为以下学习者制定一份详细的学习计划：\n\n学习目标：{{learning_goal}}\n当前水平：{{current_level}}\n可用时间：{{available_time}}\n学习偏好：{{learning_style}}\n\n请提供：\n1. 学习路径规划\n2. 分阶段目标\n3. 推荐资源\n4. 学习方法建议\n5. 进度检查点',
        'beginner', 1, 0, 0
    )
ON DUPLICATE KEY UPDATE `title` = VALUES(`title`);

-- ==========================================
-- 初始化：为现有 Prompt 创建默认分支（需手动执行）
-- ==========================================
/*
-- 为每个没有分支的 Prompt 创建默认 main 分支
INSERT INTO prompt_branch (prompt_id, name, description, is_default, created_by, created_at)
SELECT
    p.id AS prompt_id,
    'main' AS name,
    '默认分支' AS description,
    1 AS is_default,
    COALESCE(p.user_id, 1) AS created_by,
    NOW() AS created_at
FROM prompts p
WHERE p.id NOT IN (
    SELECT DISTINCT prompt_id FROM prompt_branch
);

-- 更新 prompt 表的 default_branch_id
UPDATE prompts p
INNER JOIN (
    SELECT prompt_id, MIN(id) AS default_id
    FROM prompt_branch
    WHERE is_default = 1
    GROUP BY prompt_id
) b ON p.id = b.prompt_id
SET p.default_branch_id = b.default_id;
*/

-- ==========================================
-- 完成信息
-- ==========================================
-- 数据库初始化完成！
-- 共 24 张表，包含 Prompt Git 功能