from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON, Text
from enum import Enum


class DifficultyLevel(str, Enum):
    """难度级别"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TemplateCategory(SQLModel, table=True):
    """模板分类模型"""
    __tablename__ = "template_categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    name_en: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    icon: str = Field(default="📁", max_length=50)
    parent_id: Optional[int] = Field(default=None, foreign_key="template_categories.id")
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PromptTemplate(SQLModel, table=True):
    """Prompt 模板模型"""
    __tablename__ = "prompt_templates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="template_categories.id", index=True)
    
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    content: str = Field(sa_column=Column(Text))
    
    # 变量定义
    variables: Optional[List[Dict]] = Field(default=None, sa_column=Column(JSON))
    
    # 示例数据
    example_input: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    example_output: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # 标签和分类
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    difficulty: str = Field(default="beginner", max_length=20)
    
    # 统计信息
    use_count: int = Field(default=0)
    favorite_count: int = Field(default=0)
    rating: float = Field(default=0.0)
    rating_count: int = Field(default=0)
    
    # 作者信息
    author_id: Optional[int] = Field(default=None, foreign_key="users.id")
    is_official: bool = Field(default=True)
    
    # 状态
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserTemplateFavorite(SQLModel, table=True):
    """用户模板收藏模型"""
    __tablename__ = "user_template_favorites"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    template_id: int = Field(foreign_key="prompt_templates.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TemplateRating(SQLModel, table=True):
    """模板评分模型"""
    __tablename__ = "template_ratings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    template_id: int = Field(foreign_key="prompt_templates.id", index=True)
    rating: int = Field(ge=1, le=5)  # 1-5 星
    comment: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# API 请求/响应模型
# ============================================

class TemplateCategoryResponse(SQLModel):
    """分类响应模型"""
    id: int
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    icon: str
    parent_id: Optional[int] = None
    sort_order: int
    template_count: Optional[int] = 0  # 该分类下的模板数量


class PromptTemplateResponse(SQLModel):
    """模板响应模型"""
    id: int
    category_id: int
    title: str
    description: Optional[str] = None
    content: str
    variables: Optional[List[Dict]] = None
    example_input: Optional[Dict] = None
    example_output: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: str
    use_count: int
    favorite_count: int
    rating: float
    rating_count: int
    is_official: bool
    is_featured: bool
    is_favorited: Optional[bool] = False  # 当前用户是否收藏
    created_at: datetime


class PromptTemplateListItem(SQLModel):
    """模板列表项（简化版）"""
    id: int
    category_id: int
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: str
    use_count: int
    favorite_count: int
    rating: float
    is_official: bool
    is_featured: bool
    is_favorited: Optional[bool] = False
    created_at: datetime
    updated_at: datetime


class TemplateUseRequest(SQLModel):
    """使用模板请求"""
    template_id: int
    variables: Optional[Dict[str, str]] = None  # 变量值


class TemplateRatingRequest(SQLModel):
    """评分请求"""
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=500)


class TemplateCreateRequest(SQLModel):
    """创建模板请求（用户贡献模板）"""
    category_id: int
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    content: str = Field(min_length=1)
    variables: Optional[List[Dict]] = None
    tags: Optional[List[str]] = None
    difficulty: str = "beginner"


class PromptTemplateCreate(SQLModel):
    """管理员创建模板请求"""
    category_id: int
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    content: str = Field(min_length=1)
    variables: Optional[List[Dict]] = None
    example_input: Optional[Dict] = None
    example_output: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: str = "beginner"
    is_featured: bool = False


class PromptTemplateUpdate(SQLModel):
    """管理员更新模板请求"""
    category_id: Optional[int] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    content: Optional[str] = Field(default=None, min_length=1)
    variables: Optional[List[Dict]] = None
    example_input: Optional[Dict] = None
    example_output: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None

