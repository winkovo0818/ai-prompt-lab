from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import create_db_and_tables
from .api import auth, prompt, run, abtest, ai_config, execution_history, admin, site, template, batch_test, optimization, security, system_config, file_upload, prompt_analysis, statistics, comment, team, quota

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Prompt 智能工作台 - 调试、管理、对比、分享 Prompt",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 临时允许所有来源，方便调试
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加安全中间件
from .core.access_control import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware
)

# 请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 安全响应头中间件
app.add_middleware(SecurityHeadersMiddleware)

# 频率限制中间件（调整为更宽松的限制）
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=120,  # 每分钟120次（原来60次）
    requests_per_hour=3000,   # 每小时3000次（原来1000次）
    enabled=True
)


# 注册路由
app.include_router(auth.router)
app.include_router(prompt.router)
app.include_router(run.router)
app.include_router(abtest.router)
app.include_router(batch_test.router)
app.include_router(optimization.router)
app.include_router(security.router)
app.include_router(system_config.router)
app.include_router(ai_config.router, prefix="/api/ai-config", tags=["AI配置"])
app.include_router(execution_history.router)
app.include_router(admin.router)
app.include_router(site.router)
app.include_router(template.router)
app.include_router(file_upload.router)
app.include_router(prompt_analysis.router, prefix="/api/prompt", tags=["Prompt分析"])
app.include_router(statistics.router)
app.include_router(comment.router)
app.include_router(team.router)
app.include_router(quota.router)


@app.on_event("startup")
async def on_startup():
    """应用启动时执行"""
    # 数据库初始化（如果启动时卡住，注释掉这行并手动运行 init_db.py）
    try:
        create_db_and_tables()
        print("[OK] 数据库表初始化成功")
    except Exception as e:
        print(f"[WARNING] 数据库初始化失败: {e}")
        print("   请检查数据库配置或手动运行 python init_db.py")
    
    print(f"[SUCCESS] {settings.APP_NAME} 启动成功!")
    print(f"[INFO] API 文档: http://localhost:8000/docs")


@app.get("/")
async def root():
    """根路径"""
    return {
        "code": 0,
        "message": "欢迎使用 AI Prompt Lab API",
        "data": {
            "version": "1.0.0",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "code": 0,
        "message": "服务正常",
        "data": {"status": "healthy"}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

