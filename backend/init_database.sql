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
-- 9. A/B 测试表
-- ==========================================

CREATE TABLE IF NOT EXISTS `ab_tests` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '测试 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `name` VARCHAR(200) NOT NULL COMMENT '测试名称',
    `description` TEXT NULL COMMENT '测试描述',
    `prompt_a_id` INT NOT NULL COMMENT 'Prompt A ID',
    `prompt_b_id` INT NOT NULL COMMENT 'Prompt B ID',
    `config_a_id` INT NULL COMMENT 'Prompt A 使用的 AI 配置 ID',
    `config_b_id` INT NULL COMMENT 'Prompt B 使用的 AI 配置 ID',
    `test_cases` JSON NULL COMMENT '测试用例 JSON',
    `results` JSON NULL COMMENT '测试结果 JSON',
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态: pending/running/completed/failed',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_ab_tests_user_id` (`user_id`),
    INDEX `idx_ab_tests_status` (`status`),
    INDEX `idx_ab_tests_created_at` (`created_at`),

    CONSTRAINT `fk_ab_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ab_prompt_a` FOREIGN KEY (`prompt_a_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ab_prompt_b` FOREIGN KEY (`prompt_b_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ab_config_a` FOREIGN KEY (`config_a_id`) REFERENCES `ai_configs` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_ab_config_b` FOREIGN KEY (`config_b_id`) REFERENCES `ai_configs` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='A/B 测试表';

-- ==========================================
-- 10. 执行历史表
-- ==========================================

CREATE TABLE IF NOT EXISTS `execution_history` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '记录 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `prompt_id` INT NULL COMMENT 'Prompt ID',
    `prompt_content` TEXT NOT NULL COMMENT '执行时的 Prompt 内容',
    `variables` JSON NULL COMMENT '变量值 JSON',
    `ai_config_id` INT NULL COMMENT 'AI 配置 ID',
    `model` VARCHAR(100) NULL COMMENT '使用的模型',
    `response` TEXT NULL COMMENT 'AI 响应',
    `tokens_used` INT NULL COMMENT '使用的 Token 数',
    `execution_time` REAL NULL COMMENT '执行时间（秒）',
    `status` VARCHAR(20) NOT NULL DEFAULT 'success' COMMENT '状态: success/error/partial',
    `error_message` TEXT NULL COMMENT '错误信息',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    INDEX `idx_execution_history_user_id` (`user_id`),
    INDEX `idx_execution_history_prompt_id` (`prompt_id`),
    INDEX `idx_execution_history_status` (`status`),
    INDEX `idx_execution_history_created_at` (`created_at`),

    CONSTRAINT `fk_exec_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_exec_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_exec_config` FOREIGN KEY (`ai_config_id`) REFERENCES `ai_configs` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行历史表';

-- ==========================================
-- 11. 质量评估表
-- ==========================================

CREATE TABLE IF NOT EXISTS `quality_evaluations` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '评估 ID',
    `execution_id` INT NOT NULL COMMENT '执行记录 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `rating` INT NULL COMMENT '评分 1-5',
    `feedback` TEXT NULL COMMENT '反馈内容',
    `metrics` JSON NULL COMMENT '评估指标 JSON',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (`id`),
    INDEX `idx_quality_evaluations_execution_id` (`execution_id`),
    INDEX `idx_quality_evaluations_user_id` (`user_id`),
    INDEX `idx_quality_evaluations_rating` (`rating`),

    CONSTRAINT `fk_qe_execution` FOREIGN KEY (`execution_id`) REFERENCES `execution_history` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_qe_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
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
    `site_description` TEXT NULL COMMENT '网站描述',
    `logo_url` VARCHAR(500) NULL COMMENT 'Logo URL',
    `allow_registration` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否允许注册',
    `require_email_verification` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否需要邮箱验证',
    `max_prompts_per_user` INT NOT NULL DEFAULT 1000 COMMENT '每用户最大 Prompt 数',
    `max_api_configs_per_user` INT NOT NULL DEFAULT 10 COMMENT '每用户最大 API 配置数',
    `enable_template_library` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用模板库',
    `enable_ab_testing` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用 A/B 测试',
    `default_prompt_visibility` VARCHAR(20) NOT NULL DEFAULT 'private' COMMENT '默认 Prompt 可见性: private/public',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='网站设置表';

-- ==========================================
-- 19. 团队表
-- ==========================================

CREATE TABLE IF NOT EXISTS `teams` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '团队 ID',
    `name` VARCHAR(100) NOT NULL COMMENT '团队名称',
    `description` TEXT NULL COMMENT '团队描述',
    `owner_id` INT NOT NULL COMMENT '所有者用户 ID',
    `invite_code` VARCHAR(32) NULL UNIQUE COMMENT '邀请码',
    `max_members` INT NOT NULL DEFAULT 50 COMMENT '最大成员数',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_teams_owner` (`owner_id`),
    INDEX `idx_teams_invite_code` (`invite_code`),

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
    `permission` VARCHAR(20) NOT NULL DEFAULT 'read' COMMENT '权限: read/write',
    `shared_by` INT NOT NULL COMMENT '分享人用户 ID',
    `shared_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '分享时间',

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
    `parent_id` INT NULL COMMENT '父评论 ID（用于回复）',
    `content` TEXT NOT NULL COMMENT '评论内容',
    `like_count` INT NOT NULL DEFAULT 0 COMMENT '点赞数',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    INDEX `idx_prompt_comments_prompt_id` (`prompt_id`),
    INDEX `idx_prompt_comments_user_id` (`user_id`),
    INDEX `idx_prompt_comments_parent_id` (`parent_id`),

    CONSTRAINT `fk_pc_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pc_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pc_parent` FOREIGN KEY (`parent_id`) REFERENCES `prompt_comments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt 评论表';

-- ==========================================
-- 23. 评论点赞表
-- ==========================================

CREATE TABLE IF NOT EXISTS `comment_likes` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `comment_id` INT NOT NULL COMMENT '评论 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_comment_like` (`comment_id`, `user_id`),
    INDEX `idx_comment_likes_comment_id` (`comment_id`),
    INDEX `idx_comment_likes_user_id` (`user_id`),

    CONSTRAINT `fk_cl_comment` FOREIGN KEY (`comment_id`) REFERENCES `prompt_comments` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_cl_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评论点赞表';

-- ==========================================
-- 24. 系统配额表
-- ==========================================

CREATE TABLE IF NOT EXISTS `quotas` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '配额 ID',
    `user_id` INT NOT NULL COMMENT '用户 ID',
    `quota_type` VARCHAR(50) NOT NULL COMMENT '配额类型: prompts/executions/api_calls',
    `total` INT NOT NULL DEFAULT 0 COMMENT '总额度',
    `used` INT NOT NULL DEFAULT 0 COMMENT '已使用',
    `period` VARCHAR(20) NOT NULL DEFAULT 'monthly' COMMENT '周期: daily/weekly/monthly/unlimited',
    `reset_at` DATETIME NULL COMMENT '重置时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_quota_type` (`user_id`, `quota_type`),
    INDEX `idx_quotas_user_id` (`user_id`),
    INDEX `idx_quotas_type` (`quota_type`),

    CONSTRAINT `fk_quotas_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配额表';

-- ==========================================
-- 初始数据
-- ==========================================

-- 插入默认网站设置
INSERT INTO `site_settings` (`id`, `site_name`, `site_description`)
VALUES (1, 'AI Prompt Lab', '企业级 AI 提示词管理和测试平台')
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