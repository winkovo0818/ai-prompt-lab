from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """用户模型"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    email: str = Field(index=True, unique=True, max_length=100)
    hashed_password: str = Field(max_length=255)
    api_key: Optional[str] = Field(default=None, max_length=255)
    role: str = Field(default="user", max_length=20)  # user 或 admin
    
    # 扩展个人资料字段
    nickname: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20, index=True)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    bio: Optional[str] = Field(default=None)
    company: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=200)
    
    # 登录信息
    last_login_at: Optional[datetime] = Field(default=None, index=True)
    login_count: int = Field(default=0)
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    prompts: List["Prompt"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    """用户创建模型"""
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=100)
    password: str = Field(min_length=6, max_length=50)


class UserLogin(SQLModel):
    """用户登录模型"""
    username: str
    password: str


class UserResponse(SQLModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    api_key: Optional[str] = None
    role: str = "user"
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    last_login_at: Optional[datetime] = None
    login_count: int = 0
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    """用户更新模型（管理员使用）"""
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=6, max_length=50)
    role: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = None


class UserProfileUpdate(SQLModel):
    """用户个人资料更新模型"""
    email: Optional[str] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=6, max_length=50)
    nickname: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    bio: Optional[str] = None
    company: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=200)


class Token(SQLModel):
    """Token 响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

