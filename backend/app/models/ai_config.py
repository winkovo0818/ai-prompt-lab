"""AI 配置模型"""
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class AIConfig(SQLModel, table=True):
    """AI 配置表"""
    __tablename__ = "ai_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)  # 配置名称，如 "OpenAI GPT-4"
    base_url: str = Field(max_length=500)  # API Base URL
    api_key: str = Field(max_length=500)  # API Key (加密存储)
    model: str = Field(max_length=100)  # 默认模型
    description: Optional[str] = Field(default=None, max_length=500)  # 描述
    is_default: bool = Field(default=False)  # 是否为用户的默认配置
    is_global: bool = Field(default=False)  # 是否为全局配置（管理员配置供所有用户使用）
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AIConfigCreate(SQLModel):
    """创建 AI 配置"""
    name: str
    base_url: str
    api_key: str
    model: str
    description: Optional[str] = None
    is_default: bool = False
    is_global: bool = False


class AIConfigUpdate(SQLModel):
    """更新 AI 配置"""
    name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None


class AIConfigResponse(SQLModel):
    """AI 配置响应"""
    id: int
    user_id: int
    name: str
    base_url: str
    api_key: str  # 前端显示时需要部分隐藏
    model: str
    description: Optional[str] = None
    is_default: bool = False
    is_global: bool = False
    created_at: datetime
    updated_at: datetime

