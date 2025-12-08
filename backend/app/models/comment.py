"""
Prompt 评论模型
支持评论、@提及用户、版本评审
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON, Text


class PromptComment(SQLModel, table=True):
    """Prompt 评论模型"""
    __tablename__ = "prompt_comments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_id: int = Field(foreign_key="prompts.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # 评论内容
    content: str = Field(sa_column=Column(Text))
    
    # @提及的用户ID列表
    mentioned_user_ids: Optional[List[int]] = Field(default=None, sa_column=Column(JSON))
    
    # 关联的版本号（可选，用于版本评审）
    version: Optional[int] = Field(default=None, index=True)
    
    # 回复的评论ID（用于嵌套回复）
    parent_id: Optional[int] = Field(default=None, foreign_key="prompt_comments.id", index=True)
    
    # 评论类型：comment=普通评论, review=版本评审, suggestion=建议
    comment_type: str = Field(default="comment", max_length=20)
    
    # 评审状态（仅用于版本评审）：pending=待处理, approved=已通过, rejected=已拒绝
    review_status: Optional[str] = Field(default=None, max_length=20)
    
    # 是否已编辑
    is_edited: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class PromptCommentCreate(SQLModel):
    """创建评论请求"""
    content: str
    mentioned_user_ids: Optional[List[int]] = None
    version: Optional[int] = None
    parent_id: Optional[int] = None
    comment_type: str = "comment"
    review_status: Optional[str] = None


class PromptCommentUpdate(SQLModel):
    """更新评论请求"""
    content: Optional[str] = None
    review_status: Optional[str] = None


class PromptCommentResponse(SQLModel):
    """评论响应"""
    id: int
    prompt_id: int
    user_id: int
    content: str
    mentioned_user_ids: Optional[List[int]] = None
    version: Optional[int] = None
    parent_id: Optional[int] = None
    comment_type: str
    review_status: Optional[str] = None
    is_edited: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 额外信息（API 返回时填充）
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    mentioned_users: Optional[List[dict]] = None
    replies: Optional[List["PromptCommentResponse"]] = None
    reply_count: int = 0
