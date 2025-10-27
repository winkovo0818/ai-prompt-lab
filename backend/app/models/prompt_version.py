from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, Text


class PromptVersion(SQLModel, table=True):
    """Prompt 版本历史模型"""
    __tablename__ = "prompt_versions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_id: int = Field(foreign_key="prompts.id", index=True)
    
    version: int = Field(index=True)
    title: str = Field(max_length=200)
    content: str = Field(sa_column=Column(Text))  # 使用 TEXT 类型，支持大文本
    description: Optional[str] = Field(default=None, max_length=500)
    
    change_summary: Optional[str] = Field(default=None, max_length=500)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    prompt: Optional["Prompt"] = Relationship(back_populates="versions")


class PromptVersionResponse(SQLModel):
    """Prompt 版本响应模型"""
    id: int
    prompt_id: int
    version: int
    title: str
    content: str
    description: Optional[str] = None
    change_summary: Optional[str] = None
    created_at: datetime

