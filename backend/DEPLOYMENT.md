# AI Prompt Lab 部署指南

## 📋 目录
- [环境要求](#环境要求)
- [数据库初始化](#数据库初始化)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [生产环境配置](#生产环境配置)
- [常见问题](#常见问题)

---

## 环境要求

### 后端
- Python 3.8+
- SQLite 3 或 PostgreSQL/MySQL

### 前端
- Node.js 16+
- npm 或 yarn

---

## 数据库初始化

### 方式 1: 使用 SQL 脚本（推荐）

```bash
# 进入后端目录
cd backend

# 初始化数据库
sqlite3 prompt.db < init_database.sql
```

### 方式 2: 使用 Python 脚本

```bash
cd backend
python init_db.py
```

### 验证数据库

```bash
sqlite3 prompt.db

# 查看所有表
.tables

# 查看管理员账户
SELECT * FROM users WHERE role='admin';

# 退出
.quit
```

---

## 后端部署

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 复制示例文件
cp env_example.txt .env

# 编辑配置
nano .env
```

**.env 配置内容**:

```env
# 数据库配置
DATABASE_URL=sqlite:///./prompt.db

# JWT 密钥 (生产环境请使用强密码!)
SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars

# 加密密钥 (生产环境请使用强密码!)
ENCRYPTION_KEY=your-encryption-key-change-this-in-production-32

# CORS 配置
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173

# 全局 AI 配置 (可选)
# ENABLE_DEFAULT_AI=true
# DEFAULT_AI_MODEL=gpt-3.5-turbo
# DEFAULT_AI_API_KEY=your-api-key
# DEFAULT_AI_BASE_URL=https://api.openai.com/v1
```

### 3. 生成安全密钥

```bash
# 生成 SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成 ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. 启动后端服务

**开发模式**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**生产模式**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**使用 Gunicorn (推荐)**:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 5. 测试后端

```bash
# 健康检查
curl http://localhost:8000/api/health

# API 文档
# 访问: http://localhost:8000/docs
```

---

## 前端部署

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

创建 `.env.production` 文件：

```env
VITE_API_BASE_URL=http://your-backend-domain.com
```

### 3. 构建生产版本

```bash
npm run build
```

### 4. 部署静态文件

#### 方式 1: Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/dist;
    index index.html;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 方式 2: 直接使用 Vite 预览

```bash
npm run preview
```

---

## 生产环境配置

### 1. 修改默认管理员密码

```bash
# 登录系统后，立即修改管理员密码
# 或使用 SQL 更新
sqlite3 prompt.db

UPDATE users 
SET hashed_password = '$2b$12$new_hashed_password' 
WHERE username = 'admin';
```

### 2. 安全加固

**后端 (.env)**:
```env
# 使用强密钥
SECRET_KEY=<强随机字符串-至少32位>
ENCRYPTION_KEY=<强随机字符串-32位>

# 限制 CORS
ALLOWED_ORIGINS=https://your-domain.com

# 生产模式
DEBUG=False
```

**前端**:
```env
# 使用 HTTPS
VITE_API_BASE_URL=https://api.your-domain.com
```

### 3. 使用 HTTPS

```bash
# 使用 Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

### 4. 设置系统服务

创建 systemd 服务文件 `/etc/systemd/system/aipromptlab.service`:

```ini
[Unit]
Description=AI Prompt Lab Backend
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aipromptlab
sudo systemctl start aipromptlab
sudo systemctl status aipromptlab
```

### 5. 备份配置

```bash
# 备份数据库
sqlite3 prompt.db ".backup backup_$(date +%Y%m%d).db"

# 定期备份 (添加到 crontab)
0 2 * * * sqlite3 /path/to/prompt.db ".backup /path/to/backups/prompt_$(date +\%Y\%m\%d).db"
```

---

## Docker 部署（可选）

### Dockerfile (后端)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./prompt.db
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    volumes:
      - ./backend/prompt.db:/app/prompt.db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

启动:
```bash
docker-compose up -d
```

---

## 默认账户信息

### 管理员账户
- **用户名**: `admin`
- **密码**: `admin123`
- **邮箱**: `admin@aipromptlab.com`

⚠️ **重要**: 首次登录后立即修改密码！

---

## 常见问题

### 1. 数据库连接失败

**问题**: `database is locked`

**解决**:
```bash
# 检查文件权限
chmod 666 prompt.db
chmod 777 .  # 数据库目录需要写权限
```

### 2. CORS 错误

**问题**: 前端无法访问后端 API

**解决**:
```env
# .env 中添加前端域名
ALLOWED_ORIGINS=http://localhost:5173,https://your-domain.com
```

### 3. API Key 加密失败

**问题**: `Encryption key must be 32 bytes`

**解决**:
```bash
# 确保 ENCRYPTION_KEY 正好 32 字节
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. 静态文件 404

**问题**: Logo、图片无法加载

**解决**:
```nginx
# Nginx 配置
location /logo {
    alias /path/to/frontend/dist/logo;
}
```

### 5. 迁移现有数据

如果你已有旧数据库，需要迁移:

```bash
# 备份旧数据
sqlite3 old_prompt.db .dump > backup.sql

# 初始化新数据库
sqlite3 new_prompt.db < init_database.sql

# 手动迁移数据（根据需要调整）
```

---

## 性能优化

### 1. 数据库优化

```sql
-- 定期清理
VACUUM;

-- 分析查询性能
ANALYZE;
```

### 2. 使用缓存

```bash
# 安装 Redis
sudo apt install redis-server

# 配置后端缓存
pip install redis
```

### 3. 启用 Gzip 压缩

```nginx
# Nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

---

## 监控和日志

### 查看日志

```bash
# 后端日志
tail -f /var/log/aipromptlab/backend.log

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 系统服务日志
journalctl -u aipromptlab -f
```

### 监控指标

- API 响应时间
- 数据库连接数
- 错误率
- 用户活跃度

---

## 更新部署

```bash
# 1. 备份数据库
sqlite3 prompt.db ".backup backup.db"

# 2. 拉取最新代码
git pull origin main

# 3. 更新依赖
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. 运行迁移脚本（如有）
cd ../backend
python run_migration.py

# 5. 重启服务
sudo systemctl restart aipromptlab

# 6. 重新构建前端
cd ../frontend
npm run build
```

---

## 技术支持

- 👤 作者: 云淡风轻
- 💬 QQ: 1026771081
- 🐛 问题反馈: https://github.com/winkovo0818/ai-prompt-lab/issues
- 🌐 项目地址: https://github.com/winkovo0818/ai-prompt-lab

---

**祝部署顺利！** 🚀

