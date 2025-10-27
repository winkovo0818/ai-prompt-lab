from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, JSON, Column, Text
from pydantic import field_validator


class Prompt(SQLModel, table=True):
    """Prompt 模型"""
    __tablename__ = "prompts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    title: str = Field(max_length=200)
    content: str = Field(sa_column=Column(Text))
    description: Optional[str] = Field(default=None, max_length=500)
    
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    is_public: bool = Field(default=False)
    
    version: int = Field(default=1)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    user: Optional["User"] = Relationship(back_populates="prompts")
    versions: List["PromptVersion"] = Relationship(back_populates="prompt")


class UserPromptFavorite(SQLModel, table=True):
    """用户 Prompt 收藏模型"""
    __tablename__ = "user_prompt_favorites"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    prompt_id: int = Field(foreign_key="prompts.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PromptCreate(SQLModel):
    """创建 Prompt 模型"""
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)  # 移除 max_length 限制，支持大文本
    description: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[List[str]] = None
    is_public: bool = False


class PromptUpdate(SQLModel):
    """更新 Prompt 模型"""
    title: Optional[str] = Field(default=None, max_length=200)
    content: Optional[str] = None  # 移除 max_length 限制，支持大文本
    description: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class PromptResponse(SQLModel):
    """Prompt 响应模型"""
    id: int
    user_id: int
    title: str
    content: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: bool
    is_public: bool
    version: int
    created_at: datetime
    updated_at: datetime


class PromptListItem(SQLModel):
    """Prompt 列表项模型"""
    id: int
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: bool
    is_public: bool
    version: int
    created_at: datetime
    updated_at: datetime

