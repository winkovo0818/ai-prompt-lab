"""
团队工作区模型
支持团队/组织管理、成员角色、共享 Prompt 库
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON, Text
from enum import Enum


class TeamRole(str, Enum):
    """团队角色枚举"""
    OWNER = "owner"      # 所有者：完全控制权
    EDITOR = "editor"    # 编辑者：可以创建、编辑、删除 Prompt
    VIEWER = "viewer"    # 查看者：只能查看 Prompt


class Team(SQLModel, table=True):
    """团队模型"""
    __tablename__ = "teams"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    
    # 团队创建者
    owner_id: int = Field(foreign_key="users.id", index=True)
    
    # 团队设置
    is_public: bool = Field(default=False)  # 是否公开团队
    allow_member_invite: bool = Field(default=False)  # 是否允许成员邀请他人
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TeamMember(SQLModel, table=True):
    """团队成员模型"""
    __tablename__ = "team_members"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # 成员角色
    role: str = Field(default="viewer", max_length=20)  # owner, editor, viewer
    
    # 邀请信息
    invited_by: Optional[int] = Field(default=None, foreign_key="users.id")
    invited_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 加入状态
    status: str = Field(default="active", max_length=20)  # pending, active, removed
    joined_at: Optional[datetime] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TeamPrompt(SQLModel, table=True):
    """团队 Prompt 关联模型"""
    __tablename__ = "team_prompts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", index=True)
    prompt_id: int = Field(foreign_key="prompts.id", index=True)
    
    # 共享设置
    shared_by: int = Field(foreign_key="users.id")  # 谁共享的
    permission: str = Field(default="view", max_length=20)  # view, edit
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TeamInvite(SQLModel, table=True):
    """团队邀请模型"""
    __tablename__ = "team_invites"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", index=True)
    
    # 邀请信息
    invite_code: str = Field(max_length=50, unique=True, index=True)
    email: Optional[str] = Field(default=None, max_length=100)  # 指定邮箱邀请
    role: str = Field(default="viewer", max_length=20)
    
    # 邀请者
    created_by: int = Field(foreign_key="users.id")
    
    # 有效期
    expires_at: Optional[datetime] = Field(default=None)
    max_uses: int = Field(default=1)  # 最大使用次数
    used_count: int = Field(default=0)  # 已使用次数
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== 请求/响应模型 ====================

class TeamCreate(SQLModel):
    """创建团队请求"""
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = None
    is_public: bool = False
    allow_member_invite: bool = False


class TeamUpdate(SQLModel):
    """更新团队请求"""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = None
    is_public: Optional[bool] = None
    allow_member_invite: Optional[bool] = None


class TeamMemberAdd(SQLModel):
    """添加团队成员请求"""
    user_id: Optional[int] = None  # 直接添加用户
    email: Optional[str] = None  # 通过邮箱邀请
    role: str = "viewer"


class TeamMemberUpdate(SQLModel):
    """更新团队成员请求"""
    role: str


class TeamPromptShare(SQLModel):
    """共享 Prompt 到团队请求"""
    prompt_id: int
    permission: str = "view"  # view, edit


class TeamInviteCreate(SQLModel):
    """创建邀请链接请求"""
    role: str = "viewer"
    expires_hours: Optional[int] = 72  # 过期时间（小时）
    max_uses: int = 10


class TeamResponse(SQLModel):
    """团队响应"""
    id: int
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    owner_id: int
    is_public: bool
    allow_member_invite: bool
    member_count: int = 0
    prompt_count: int = 0
    my_role: Optional[str] = None  # 当前用户在团队中的角色
    created_at: datetime
    updated_at: datetime


class TeamMemberResponse(SQLModel):
    """团队成员响应"""
    id: int
    team_id: int
    user_id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    role: str
    status: str
    joined_at: Optional[datetime] = None
    invited_by_username: Optional[str] = None


class TeamPromptResponse(SQLModel):
    """团队 Prompt 响应"""
    id: int
    team_id: int
    prompt_id: int
    prompt_title: str
    prompt_description: Optional[str] = None
    permission: str
    shared_by_username: str
    created_at: datetime
