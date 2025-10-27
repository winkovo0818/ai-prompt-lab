"""Prompt 模板 API"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, or_

from ..models.user import User
from ..models.template import (
    TemplateCategory, PromptTemplate, UserTemplateFavorite, TemplateRating,
    TemplateCategoryResponse, PromptTemplateResponse, PromptTemplateListItem,
    TemplateUseRequest, TemplateRatingRequest, TemplateCreateRequest
)
from ..models.prompt import Prompt, PromptCreate
from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..utils.response import success_response, error_response

router = APIRouter(prefix="/api/template", tags=["模板"])


@router.get("/categories")
async def get_categories(
    db: Session = Depends(get_session)
):
    """获取所有分类（树形结构）"""
    # 获取所有分类
    statement = select(TemplateCategory).where(TemplateCategory.is_active == True).order_by(
        TemplateCategory.sort_order
    )
    categories = db.exec(statement).all()
    
    # 统计每个分类下的模板数量
    category_counts = {}
    for category in categories:
        count_statement = select(func.count(PromptTemplate.id)).where(
            PromptTemplate.category_id == category.id,
            PromptTemplate.is_active == True
        )
        count = db.exec(count_statement).one()
        category_counts[category.id] = count
    
    # 构建响应
    result = []
    for category in categories:
        result.append(TemplateCategoryResponse(
            id=category.id,
            name=category.name,
            name_en=category.name_en,
            description=category.description,
            icon=category.icon,
            parent_id=category.parent_id,
            sort_order=category.sort_order,
            template_count=category_counts.get(category.id, 0)
        ))
    
    return success_response(data=result)


@router.get("/list")
async def get_templates(
    category_id: Optional[int] = Query(None, description="分类ID"),
    difficulty: Optional[str] = Query(None, description="难度级别"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    is_featured: Optional[bool] = Query(None, description="是否精选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取模板列表"""
    # 构建查询
    statement = select(PromptTemplate).where(PromptTemplate.is_active == True)
    
    # 分类筛选
    if category_id:
        statement = statement.where(PromptTemplate.category_id == category_id)
    
    # 难度筛选
    if difficulty:
        statement = statement.where(PromptTemplate.difficulty == difficulty)
    
    # 精选筛选
    if is_featured is not None:
        statement = statement.where(PromptTemplate.is_featured == is_featured)
    
    # 搜索
    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                PromptTemplate.title.like(search_pattern),
                PromptTemplate.description.like(search_pattern)
            )
        )
    
    # 排序：精选优先，然后按使用次数和评分
    statement = statement.order_by(
        PromptTemplate.is_featured.desc(),
        PromptTemplate.rating.desc(),
        PromptTemplate.use_count.desc()
    )
    
    # 总数
    count_statement = select(func.count()).select_from(statement.subquery())
    total = db.exec(count_statement).one()
    
    # 分页
    statement = statement.offset((page - 1) * page_size).limit(page_size)
    templates = db.exec(statement).all()
    
    # 获取当前用户的收藏列表
    favorite_statement = select(UserTemplateFavorite.template_id).where(
        UserTemplateFavorite.user_id == current_user.id
    )
    favorited_ids = set(db.exec(favorite_statement).all())
    
    # 构建响应
    result = []
    for template in templates:
        result.append(PromptTemplateListItem(
            id=template.id,
            category_id=template.category_id,
            title=template.title,
            description=template.description,
            tags=template.tags,
            difficulty=template.difficulty,
            use_count=template.use_count,
            favorite_count=template.favorite_count,
            rating=template.rating,
            is_official=template.is_official,
            is_featured=template.is_featured,
            is_favorited=template.id in favorited_ids,
            created_at=template.created_at,
            updated_at=template.updated_at
        ))
    
    return success_response(data={
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    })


@router.get("/{template_id}")
async def get_template_detail(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取模板详情"""
    template = db.get(PromptTemplate, template_id)
    if not template or not template.is_active:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 检查是否收藏
    favorite_statement = select(UserTemplateFavorite).where(
        UserTemplateFavorite.user_id == current_user.id,
        UserTemplateFavorite.template_id == template_id
    )
    is_favorited = db.exec(favorite_statement).first() is not None
    
    return success_response(data=PromptTemplateResponse(
        id=template.id,
        category_id=template.category_id,
        title=template.title,
        description=template.description,
        content=template.content,
        variables=template.variables,
        example_input=template.example_input,
        example_output=template.example_output,
        tags=template.tags,
        difficulty=template.difficulty,
        use_count=template.use_count,
        favorite_count=template.favorite_count,
        rating=template.rating,
        rating_count=template.rating_count,
        is_official=template.is_official,
        is_featured=template.is_featured,
        is_favorited=is_favorited,
        created_at=template.created_at
    ))


@router.post("/{template_id}/use")
async def use_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """使用模板（复制到我的 Prompt）"""
    # 获取模板
    template = db.get(PromptTemplate, template_id)
    if not template or not template.is_active:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 创建新的 Prompt
    new_prompt = Prompt(
        user_id=current_user.id,
        title=f"{template.title}（副本）",
        content=template.content,
        description=template.description,
        tags=template.tags,
        is_public=False,
        is_favorite=False
    )
    
    db.add(new_prompt)
    
    # 增加使用次数
    template.use_count += 1
    db.add(template)
    
    db.commit()
    db.refresh(new_prompt)
    
    return success_response(
        data={
            "prompt_id": new_prompt.id,
            "variables": template.variables  # 返回变量配置
        },
        message="模板已复制到您的 Prompt 列表"
    )


@router.post("/{template_id}/favorite")
async def toggle_favorite(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """切换收藏状态"""
    # 检查模板是否存在
    template = db.get(PromptTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 检查是否已收藏
    statement = select(UserTemplateFavorite).where(
        UserTemplateFavorite.user_id == current_user.id,
        UserTemplateFavorite.template_id == template_id
    )
    favorite = db.exec(statement).first()
    
    if favorite:
        # 取消收藏
        db.delete(favorite)
        template.favorite_count = max(0, template.favorite_count - 1)
        message = "已取消收藏"
        is_favorited = False
    else:
        # 添加收藏
        favorite = UserTemplateFavorite(
            user_id=current_user.id,
            template_id=template_id
        )
        db.add(favorite)
        template.favorite_count += 1
        message = "已添加收藏"
        is_favorited = True
    
    db.add(template)
    db.commit()
    
    return success_response(
        data={"is_favorited": is_favorited},
        message=message
    )


@router.get("/favorites/list")
async def get_my_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取我的收藏"""
    # 查询收藏的模板ID
    statement = select(UserTemplateFavorite.template_id).where(
        UserTemplateFavorite.user_id == current_user.id
    ).order_by(UserTemplateFavorite.created_at.desc())
    
    # 总数
    count_statement = select(func.count()).select_from(statement.subquery())
    total = db.exec(count_statement).one()
    
    # 分页
    statement = statement.offset((page - 1) * page_size).limit(page_size)
    template_ids = db.exec(statement).all()
    
    if not template_ids:
        return success_response(data={
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0
        })
    
    # 获取模板详情
    templates_statement = select(PromptTemplate).where(
        PromptTemplate.id.in_(template_ids),
        PromptTemplate.is_active == True
    )
    templates = db.exec(templates_statement).all()
    
    # 构建响应
    result = []
    for template in templates:
        result.append(PromptTemplateListItem(
            id=template.id,
            category_id=template.category_id,
            title=template.title,
            description=template.description,
            tags=template.tags,
            difficulty=template.difficulty,
            use_count=template.use_count,
            favorite_count=template.favorite_count,
            rating=template.rating,
            is_official=template.is_official,
            is_featured=template.is_featured,
            is_favorited=True,
            created_at=template.created_at,
            updated_at=template.updated_at
        ))
    
    return success_response(data={
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    })


@router.post("/{template_id}/rate")
async def rate_template(
    template_id: int,
    data: TemplateRatingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """给模板评分"""
    # 检查模板是否存在
    template = db.get(PromptTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 检查是否已评分
    statement = select(TemplateRating).where(
        TemplateRating.user_id == current_user.id,
        TemplateRating.template_id == template_id
    )
    existing_rating = db.exec(statement).first()
    
    if existing_rating:
        # 更新评分
        old_rating = existing_rating.rating
        existing_rating.rating = data.rating
        existing_rating.comment = data.comment
        existing_rating.updated_at = datetime.utcnow()
        db.add(existing_rating)
        
        # 更新模板平均评分
        template.rating = template.rating + (data.rating - old_rating) / template.rating_count
    else:
        # 新增评分
        new_rating = TemplateRating(
            user_id=current_user.id,
            template_id=template_id,
            rating=data.rating,
            comment=data.comment
        )
        db.add(new_rating)
        
        # 更新模板平均评分
        total_rating = template.rating * template.rating_count + data.rating
        template.rating_count += 1
        template.rating = total_rating / template.rating_count
    
    db.add(template)
    db.commit()
    
    return success_response(message="评分成功")


@router.post("/create")
async def create_template(
    data: TemplateCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """用户贡献模板"""
    # 检查分类是否存在
    category = db.get(TemplateCategory, data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 创建模板（需要管理员审核）
    template = PromptTemplate(
        category_id=data.category_id,
        title=data.title,
        description=data.description,
        content=data.content,
        variables=data.variables,
        tags=data.tags,
        difficulty=data.difficulty,
        author_id=current_user.id,
        is_official=False,
        is_active=False  # 默认不激活，需要审核
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return success_response(
        data={"template_id": template.id},
        message="模板已提交，等待管理员审核"
    )


@router.get("/stats/popular")
async def get_popular_templates(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_session)
):
    """获取热门模板"""
    statement = select(PromptTemplate).where(
        PromptTemplate.is_active == True
    ).order_by(
        PromptTemplate.use_count.desc()
    ).limit(limit)
    
    templates = db.exec(statement).all()
    
    result = []
    for template in templates:
        result.append({
            "id": template.id,
            "title": template.title,
            "use_count": template.use_count,
            "rating": template.rating
        })
    
    return success_response(data=result)

