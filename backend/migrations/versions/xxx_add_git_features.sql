-- ============================================
-- AI Prompt Lab - Prompt Git 化数据库迁移
-- ============================================
-- 这是一个完整的数据库迁移脚本
-- 适用于 MySQL 5.7+

-- ============================================
-- 1. 修改 prompt 表 - 添加默认分支字段
-- ============================================
ALTER TABLE `prompt`
ADD COLUMN `default_branch_id` INT NULL
COMMENT '默认分支 ID'
AFTER `content`;

-- 添加索引
ALTER TABLE `prompt`
ADD INDEX `idx_prompt_default_branch` (`default_branch_id`);

-- ============================================
-- 2. 创建 prompt_branch 表
-- ============================================
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

    CONSTRAINT `fk_branch_prompt` FOREIGN KEY (`prompt_id`)
        REFERENCES `prompt` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_branch_base` FOREIGN KEY (`base_branch_id`)
        REFERENCES `prompt_branch` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_branch_creator` FOREIGN KEY (`created_by`)
        REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Prompt 分支表';

-- ============================================
-- 3. 创建 prompt_commit 表
-- ============================================
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

    CONSTRAINT `fk_commit_branch` FOREIGN KEY (`branch_id`)
        REFERENCES `prompt_branch` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_commit_parent` FOREIGN KEY (`parent_id`)
        REFERENCES `prompt_commit` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_commit_creator` FOREIGN KEY (`created_by`)
        REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Prompt 提交记录表';

-- ============================================
-- 4. 创建 prompt_pull_request 表
-- ============================================
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

    CONSTRAINT `fk_pr_prompt` FOREIGN KEY (`prompt_id`)
        REFERENCES `prompt` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_pr_source` FOREIGN KEY (`source_branch_id`)
        REFERENCES `prompt_branch` (`id`),
    CONSTRAINT `fk_pr_target` FOREIGN KEY (`target_branch_id`)
        REFERENCES `prompt_branch` (`id`),
    CONSTRAINT `fk_pr_author` FOREIGN KEY (`author_id`)
        REFERENCES `user` (`id`),
    CONSTRAINT `fk_pr_reviewer` FOREIGN KEY (`reviewer_id`)
        REFERENCES `user` (`id`),
    CONSTRAINT `fk_pr_merger` FOREIGN KEY (`merged_by`)
        REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Prompt Pull Request 表';

-- ============================================
-- 5. 回滚脚本
-- ============================================
-- 如需回滚，执行以下 SQL：

/*
-- 删除 PR 表
DROP TABLE IF EXISTS `prompt_prompt_request`;

-- 删除 commit 表
DROP TABLE IF EXISTS `prompt_commit`;

-- 删除 branch 表
DROP TABLE IF EXISTS `prompt_branch`;

-- 移除 prompt 表字段
ALTER TABLE `prompt`
DROP COLUMN `default_branch_id`;

ALTER TABLE `prompt`
DROP INDEX `idx_prompt_default_branch`;
*/

-- ============================================
-- 6. 初始化：为现有 Prompt 创建默认分支
-- ============================================
-- 以下 SQL 用于为现有 Prompt 创建 main 分支
-- 建议在迁移后手动执行一次

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
FROM prompt p
WHERE p.id NOT IN (
    SELECT DISTINCT prompt_id FROM prompt_branch
);

-- 更新 prompt 表的 default_branch_id
UPDATE prompt p
INNER JOIN (
    SELECT prompt_id, MIN(id) AS default_id
    FROM prompt_branch
    WHERE is_default = 1
    GROUP BY prompt_id
) b ON p.id = b.prompt_id
SET p.default_branch_id = b.default_id;
*/