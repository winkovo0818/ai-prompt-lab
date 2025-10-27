-- 创建用户 Prompt 收藏表
CREATE TABLE IF NOT EXISTS user_prompt_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    UNIQUE(user_id, prompt_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_prompt_favorites_user_id ON user_prompt_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_prompt_favorites_prompt_id ON user_prompt_favorites(prompt_id);

-- 迁移现有数据：将 is_favorite=1 的记录转换到新表
INSERT INTO user_prompt_favorites (user_id, prompt_id, created_at)
SELECT user_id, id, created_at
FROM prompts
WHERE is_favorite = 1;

-- 删除旧的 is_favorite 字段（SQLite 需要重建表）
-- 1. 创建新表
CREATE TABLE prompts_new (
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

-- 2. 复制数据
INSERT INTO prompts_new (id, user_id, title, content, description, tags, is_public, version, created_at, updated_at)
SELECT id, user_id, title, content, description, tags, is_public, version, created_at, updated_at
FROM prompts;

-- 3. 删除旧表
DROP TABLE prompts;

-- 4. 重命名新表
ALTER TABLE prompts_new RENAME TO prompts;

-- 5. 重建索引
CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON prompts(user_id);

