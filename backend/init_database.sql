-- ==========================================
-- AI Prompt Lab 数据库初始化脚本
-- 版本: 1.0
-- 日期: 2025-10-27
-- 说明: 包含所有表结构、索引、初始数据
-- ==========================================

-- ==========================================
-- 1. 用户表
-- ==========================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(500),
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ==========================================
-- 2. Prompt 表
-- ==========================================

CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    description VARCHAR(500),
    tags TEXT,
    is_public BOOLEAN NOT NULL DEFAULT 0,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON prompts(user_id);
CREATE INDEX IF NOT EXISTS idx_prompts_is_public ON prompts(is_public);
CREATE INDEX IF NOT EXISTS idx_prompts_updated_at ON prompts(updated_at);

-- ==========================================
-- 3. 用户 Prompt 收藏表
-- ==========================================

CREATE TABLE IF NOT EXISTS user_prompt_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    UNIQUE(user_id, prompt_id)
);

CREATE INDEX IF NOT EXISTS idx_user_prompt_favorites_user_id ON user_prompt_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_prompt_favorites_prompt_id ON user_prompt_favorites(prompt_id);

-- ==========================================
-- 4. Prompt 版本历史表
-- ==========================================

CREATE TABLE IF NOT EXISTS prompt_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    description VARCHAR(500),
    change_summary VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    UNIQUE(prompt_id, version)
);

CREATE INDEX IF NOT EXISTS idx_prompt_versions_prompt_id ON prompt_versions(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_version ON prompt_versions(version);

-- ==========================================
-- 5. AI 配置表
-- ==========================================

CREATE TABLE IF NOT EXISTS ai_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name VARCHAR(100) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    api_key VARCHAR(500) NOT NULL,
    model VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    is_default BOOLEAN NOT NULL DEFAULT 0,
    is_global BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ai_configs_user_id ON ai_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_configs_is_default ON ai_configs(is_default);
CREATE INDEX IF NOT EXISTS idx_ai_configs_is_global ON ai_configs(is_global);

-- ==========================================
-- 6. A/B 测试表
-- ==========================================

CREATE TABLE IF NOT EXISTS ab_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    prompt_a_id INTEGER NOT NULL,
    prompt_b_id INTEGER NOT NULL,
    config_a_id INTEGER,
    config_b_id INTEGER,
    test_cases TEXT,
    results TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (prompt_a_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (prompt_b_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (config_a_id) REFERENCES ai_configs(id) ON DELETE SET NULL,
    FOREIGN KEY (config_b_id) REFERENCES ai_configs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_ab_tests_user_id ON ab_tests(user_id);
CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON ab_tests(status);
CREATE INDEX IF NOT EXISTS idx_ab_tests_created_at ON ab_tests(created_at);

-- ==========================================
-- 7. 执行历史表
-- ==========================================

CREATE TABLE IF NOT EXISTS execution_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt_id INTEGER,
    prompt_content TEXT NOT NULL,
    variables TEXT,
    ai_config_id INTEGER,
    model VARCHAR(100),
    response TEXT,
    tokens_used INTEGER,
    execution_time REAL,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE SET NULL,
    FOREIGN KEY (ai_config_id) REFERENCES ai_configs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_execution_history_user_id ON execution_history(user_id);
CREATE INDEX IF NOT EXISTS idx_execution_history_prompt_id ON execution_history(prompt_id);
CREATE INDEX IF NOT EXISTS idx_execution_history_status ON execution_history(status);
CREATE INDEX IF NOT EXISTS idx_execution_history_created_at ON execution_history(created_at);

-- ==========================================
-- 8. 质量评估表
-- ==========================================

CREATE TABLE IF NOT EXISTS quality_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER,
    feedback TEXT,
    metrics TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES execution_history(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_quality_evaluations_execution_id ON quality_evaluations(execution_id);
CREATE INDEX IF NOT EXISTS idx_quality_evaluations_user_id ON quality_evaluations(user_id);
CREATE INDEX IF NOT EXISTS idx_quality_evaluations_rating ON quality_evaluations(rating);

-- ==========================================
-- 9. 模板分类表
-- ==========================================

CREATE TABLE IF NOT EXISTS template_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description VARCHAR(500),
    icon VARCHAR(50) NOT NULL DEFAULT '📁',
    parent_id INTEGER,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES template_categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_template_categories_parent_id ON template_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_template_categories_sort_order ON template_categories(sort_order);

-- ==========================================
-- 10. Prompt 模板表
-- ==========================================

CREATE TABLE IF NOT EXISTS prompt_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(500),
    content TEXT NOT NULL,
    variables TEXT,
    example_input TEXT,
    example_output TEXT,
    tags TEXT,
    difficulty VARCHAR(20) NOT NULL DEFAULT 'beginner',
    use_count INTEGER NOT NULL DEFAULT 0,
    favorite_count INTEGER NOT NULL DEFAULT 0,
    rating REAL NOT NULL DEFAULT 0.0,
    rating_count INTEGER NOT NULL DEFAULT 0,
    author_id INTEGER,
    is_official BOOLEAN NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    is_featured BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES template_categories(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_prompt_templates_category_id ON prompt_templates(category_id);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_difficulty ON prompt_templates(difficulty);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_is_featured ON prompt_templates(is_featured);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_use_count ON prompt_templates(use_count);

-- ==========================================
-- 11. 用户模板收藏表
-- ==========================================

CREATE TABLE IF NOT EXISTS user_template_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES prompt_templates(id) ON DELETE CASCADE,
    UNIQUE(user_id, template_id)
);

CREATE INDEX IF NOT EXISTS idx_user_template_favorites_user_id ON user_template_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_template_favorites_template_id ON user_template_favorites(template_id);

-- ==========================================
-- 12. 模板评分表
-- ==========================================

CREATE TABLE IF NOT EXISTS template_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES prompt_templates(id) ON DELETE CASCADE,
    UNIQUE(user_id, template_id)
);

CREATE INDEX IF NOT EXISTS idx_template_ratings_template_id ON template_ratings(template_id);
CREATE INDEX IF NOT EXISTS idx_template_ratings_user_id ON template_ratings(user_id);

-- ==========================================
-- 13. 敏感词表
-- ==========================================

CREATE TABLE IF NOT EXISTS sensitive_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sensitive_words_word ON sensitive_words(word);
CREATE INDEX IF NOT EXISTS idx_sensitive_words_category ON sensitive_words(category);
CREATE INDEX IF NOT EXISTS idx_sensitive_words_is_active ON sensitive_words(is_active);

-- ==========================================
-- 14. 审计日志表
-- ==========================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    details TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- ==========================================
-- 15. 网站设置表
-- ==========================================

CREATE TABLE IF NOT EXISTS site_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_name VARCHAR(100) NOT NULL DEFAULT 'AI Prompt Lab',
    site_description TEXT,
    allow_registration BOOLEAN NOT NULL DEFAULT 1,
    require_email_verification BOOLEAN NOT NULL DEFAULT 0,
    max_prompts_per_user INTEGER NOT NULL DEFAULT 1000,
    max_api_configs_per_user INTEGER NOT NULL DEFAULT 10,
    enable_template_library BOOLEAN NOT NULL DEFAULT 1,
    enable_ab_testing BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 初始数据
-- ==========================================

-- 插入默认网站设置
INSERT OR IGNORE INTO site_settings (id, site_name, site_description)
VALUES (1, 'AI Prompt Lab', '专业的 AI 提示词管理和测试平台');

-- 插入默认管理员账户
-- 用户名: admin
-- 密码: admin123 (请在生产环境中立即修改!)
-- 密码哈希是使用 bcrypt 生成的 "admin123"
INSERT OR IGNORE INTO users (id, username, email, hashed_password, full_name, role, is_active)
VALUES (
    1, 
    'admin', 
    'admin@aipromptlab.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIvAprzm3u',
    '系统管理员',
    'admin',
    1
);

-- 插入默认模板分类
INSERT OR IGNORE INTO template_categories (id, name, name_en, description, icon, sort_order)
VALUES 
    (1, '文案创作', 'Copywriting', '各类文案、广告、营销内容创作', '✍️', 1),
    (2, '代码开发', 'Coding', '代码生成、调试、优化相关', '💻', 2),
    (3, '数据分析', 'Data Analysis', '数据处理、分析、可视化', '📊', 3),
    (4, '教育培训', 'Education', '教学、培训、学习相关', '📚', 4),
    (5, '商业分析', 'Business', '商业策略、市场分析', '💼', 5),
    (6, '创意设计', 'Creative', '创意构思、设计灵感', '🎨', 6);

-- 插入示例模板
INSERT OR IGNORE INTO prompt_templates (
    id, category_id, title, description, content, 
    difficulty, is_official, is_featured, use_count
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
    );

-- ==========================================
-- 完成信息
-- ==========================================

-- 查询统计信息
SELECT 
    '数据库初始化完成！' as message,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='table') as total_tables,
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM template_categories) as total_categories,
    (SELECT COUNT(*) FROM prompt_templates) as total_templates;

