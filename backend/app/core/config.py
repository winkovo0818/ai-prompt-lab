from pydantic_settings import BaseSettings
from typing import Optional, List, Union
from pydantic import field_validator


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "AI Prompt Lab"
    DEBUG: bool = True

    # 数据库配置（使用 utf8mb4 支持 emoji）
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/ai_prompt_lab?charset=utf8mb4"

    # JWT 配置 - 重要：生产环境请务必使用强随机字符串
    SECRET_KEY: str = ""  # 必须从环境变量或 .env 文件读取
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天

    # CORS 配置
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:5173,http://localhost:3000"

    # 全局默认AI配置（当用户未配置时使用）
    DEFAULT_AI_PROVIDER: str = "openai"
    DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_AI_API_KEY: Optional[str] = None
    DEFAULT_AI_BASE_URL: str = "https://api.openai.com/v1"
    ENABLE_DEFAULT_AI: bool = False

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """解析 CORS_ORIGINS，支持逗号分隔的字符串或列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 启动时检查关键配置（可选，DEBUG模式下才检查）
import os
if settings.DEBUG and not os.path.exists(".env"):
    print("[WARNING] 未找到 .env 文件，部分功能可能无法正常工作")

