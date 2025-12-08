from pydantic_settings import BaseSettings
from typing import Optional, List, Union
from pydantic import field_validator


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "AI Prompt Lab"
    DEBUG: bool = True
    
    # 数据库配置（使用 utf8mb4 支持 emoji）
    DATABASE_URL: str = "mysql+pymysql://root:admin1020@localhost:3306/ai_prompt_lab?charset=utf8mb4"
    
    # JWT 配置
    SECRET_KEY: str = "9GdpDB7b7lO1CawehX4VUlVU4Q5E565LUEtH0-LzH6o"  # 使用 secrets.token_urlsafe(32) 生成
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天（原30分钟太短）
    
    # CORS 配置
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://127.0.0.1:3000"
    
    # 全局默认AI配置（当用户未配置时使用）
    DEFAULT_AI_PROVIDER: str = "openai"
    DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_AI_API_KEY: Optional[str] = None  # 从环境变量读取
    DEFAULT_AI_BASE_URL: str = "https://api.openai.com/v1"
    ENABLE_DEFAULT_AI: bool = False  # 是否启用全局默认AI
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """解析 CORS_ORIGINS，支持逗号分隔的字符串或列表"""
        if isinstance(v, str):
            # 如果是字符串，按逗号分割
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        elif isinstance(v, list):
            # 如果已经是列表，直接返回
            return v
        return ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

