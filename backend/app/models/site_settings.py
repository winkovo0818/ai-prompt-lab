from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class SiteSettings(SQLModel, table=True):
    """网站设置模型"""
    __tablename__ = "site_settings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    site_name: str = Field(default="AI Prompt Lab", max_length=100)
    site_description: str = Field(default="AI Prompt 智能工作台", max_length=500)
    site_keywords: str = Field(default="AI, Prompt, 工作台", max_length=200)
    
    page_size: int = Field(default=20)
    allow_register: bool = Field(default=True)
    default_public: bool = Field(default=False)
    
    enable_market: bool = Field(default=True)
    enable_abtest: bool = Field(default=True)
    max_abtest_prompts: int = Field(default=5)
    
    version: str = Field(default="1.0.0", max_length=20)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    

class SiteSettingsUpdate(SQLModel):
    """网站设置更新模型"""
    site_name: Optional[str] = Field(default=None, max_length=100)
    site_description: Optional[str] = Field(default=None, max_length=500)
    site_keywords: Optional[str] = Field(default=None, max_length=200)
    
    page_size: Optional[int] = None
    allow_register: Optional[bool] = None
    default_public: Optional[bool] = None
    
    enable_market: Optional[bool] = None
    enable_abtest: Optional[bool] = None
    max_abtest_prompts: Optional[int] = None


class SiteSettingsResponse(SQLModel):
    """网站设置响应模型"""
    id: int
    site_name: str
    site_description: str
    site_keywords: str
    page_size: int
    allow_register: bool
    default_public: bool
    enable_market: bool
    enable_abtest: bool
    max_abtest_prompts: int
    version: str
    updated_at: datetime

