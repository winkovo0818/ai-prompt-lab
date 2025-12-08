from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select
from ..core.database import get_session
from ..core.deps import get_current_admin_user
from ..core.security import get_password_hash
from ..models.user import User, UserResponse, UserUpdate, UserCreate
from ..models.prompt import Prompt
from ..models.site_settings import SiteSettings, SiteSettingsUpdate, SiteSettingsResponse
from ..models.template import PromptTemplate, PromptTemplateCreate, PromptTemplateUpdate
from ..models.team import Team, TeamMember, TeamPrompt
from ..utils.response import success_response, error_response

router = APIRouter(prefix="/api/admin", tags=["管理员"])


# ==================== 用户管理 ====================

@router.get("/users", response_model=dict)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """获取用户列表（管理员）"""
    query = select(User)
    
    # 搜索过滤
    if search:
        query = query.where(
            (User.username.contains(search)) | 
            (User.email.contains(search))
        )
    
    # 角色过滤
    if role:
        query = query.where(User.role == role)
    
    # 分页
    total_query = select(User).where(*query.whereclause.clauses if query.whereclause is not None else [])
    total = len(db.exec(total_query).all())
    
    users = db.exec(query.offset(skip).limit(limit)).all()
    
    # 转换为响应模型
    user_responses = [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            api_key=user.api_key,
            role=user.role,
            nickname=user.nickname,
            phone=user.phone,
            avatar_url=user.avatar_url,
            bio=user.bio,
            company=user.company,
            location=user.location,
            website=user.website,
            last_login_at=user.last_login_at,
            login_count=user.login_count,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]
    
    return success_response(data={
        "items": user_responses,
        "total": total,
        "skip": skip,
        "limit": limit
    })


@router.get("/users/{user_id}", response_model=dict)
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """获取用户详情（管理员）"""
    user = db.get(User, user_id)
    
    if not user:
        return error_response(code=2001, message="用户不存在")
    
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        api_key=user.api_key,
        role=user.role,
        nickname=user.nickname,
        phone=user.phone,
        avatar_url=user.avatar_url,
        bio=user.bio,
        company=user.company,
        location=user.location,
        website=user.website,
        last_login_at=user.last_login_at,
        login_count=user.login_count,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return success_response(data=user_response)


@router.post("/users", response_model=dict)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """创建用户（管理员）"""
    # 检查用户名是否存在
    existing_user = db.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    
    if existing_user:
        return error_response(code=1001, message="用户名已存在")
    
    # 检查邮箱是否存在
    existing_email = db.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    
    if existing_email:
        return error_response(code=1002, message="邮箱已被使用")
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role="user"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    user_response = UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        api_key=new_user.api_key,
        role=new_user.role,
        nickname=new_user.nickname,
        phone=new_user.phone,
        avatar_url=new_user.avatar_url,
        bio=new_user.bio,
        company=new_user.company,
        location=new_user.location,
        website=new_user.website,
        last_login_at=new_user.last_login_at,
        login_count=new_user.login_count,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )
    
    return success_response(data=user_response, message="用户创建成功")


@router.put("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """更新用户（管理员）"""
    user = db.get(User, user_id)
    
    if not user:
        return error_response(code=2001, message="用户不存在")
    
    # 防止修改自己的角色
    if user.id == current_user.id and user_data.role and user_data.role != current_user.role:
        return error_response(code=4003, message="不能修改自己的角色")
    
    # 更新字段
    if user_data.username:
        # 检查用户名是否已被使用
        existing = db.exec(
            select(User).where(User.username == user_data.username, User.id != user_id)
        ).first()
        if existing:
            return error_response(code=1001, message="用户名已存在")
        user.username = user_data.username
    
    if user_data.email:
        # 检查邮箱是否已被使用
        existing = db.exec(
            select(User).where(User.email == user_data.email, User.id != user_id)
        ).first()
        if existing:
            return error_response(code=1002, message="邮箱已被使用")
        user.email = user_data.email
    
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    
    if user_data.role:
        user.role = user_data.role
    
    if user_data.is_active is not None:
        # 防止禁用自己
        if user.id == current_user.id and not user_data.is_active:
            return error_response(code=4004, message="不能禁用自己的账户")
        user.is_active = user_data.is_active
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        api_key=user.api_key,
        role=user.role,
        nickname=user.nickname,
        phone=user.phone,
        avatar_url=user.avatar_url,
        bio=user.bio,
        company=user.company,
        location=user.location,
        website=user.website,
        last_login_at=user.last_login_at,
        login_count=user.login_count,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return success_response(data=user_response, message="用户更新成功")


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """删除用户（管理员）"""
    user = db.get(User, user_id)
    
    if not user:
        return error_response(code=2001, message="用户不存在")
    
    # 防止删除自己
    if user.id == current_user.id:
        return error_response(code=4005, message="不能删除自己的账户")
    
    db.delete(user)
    db.commit()
    
    return success_response(message="用户删除成功")


# ==================== Prompt 管理 ====================

@router.get("/prompts", response_model=dict)
async def get_all_prompts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """获取所有Prompt列表（管理员）"""
    query = select(Prompt)
    
    # 搜索过滤
    if search:
        query = query.where(
            (Prompt.title.contains(search)) | 
            (Prompt.description.contains(search))
        )
    
    # 用户过滤
    if user_id:
        query = query.where(Prompt.user_id == user_id)
    
    # 公开性过滤
    if is_public is not None:
        query = query.where(Prompt.is_public == is_public)
    
    # 获取总数
    total_query = select(Prompt).where(*query.whereclause.clauses if query.whereclause is not None else [])
    total = len(db.exec(total_query).all())
    
    # 分页查询
    prompts = db.exec(query.offset(skip).limit(limit)).all()
    
    # 转换为字典并添加用户信息
    prompt_list = []
    for prompt in prompts:
        prompt_dict = prompt.model_dump()
        # 添加用户名
        user = db.get(User, prompt.user_id)
        prompt_dict['username'] = user.username if user else "未知用户"
        prompt_list.append(prompt_dict)
    
    return success_response(data={
        "items": prompt_list,
        "total": total,
        "skip": skip,
        "limit": limit
    })


@router.delete("/prompts/{prompt_id}", response_model=dict)
async def delete_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """删除Prompt（管理员）"""
    prompt = db.get(Prompt, prompt_id)
    
    if not prompt:
        return error_response(code=2001, message="Prompt 不存在")
    
    db.delete(prompt)
    db.commit()
    
    return success_response(message="Prompt 删除成功")


@router.put("/prompts/{prompt_id}/public", response_model=dict)
async def toggle_prompt_public(
    prompt_id: int,
    is_public: bool,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """切换Prompt公开状态（管理员）"""
    prompt = db.get(Prompt, prompt_id)
    
    if not prompt:
        return error_response(code=2001, message="Prompt 不存在")
    
    prompt.is_public = is_public
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    
    return success_response(
        data=prompt.model_dump(),
        message=f"Prompt 已{'公开' if is_public else '设为私有'}"
    )


# ==================== 网站设置 ====================

@router.get("/site-settings", response_model=dict)
async def get_site_settings(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """获取网站设置（管理员）"""
    settings = db.exec(select(SiteSettings)).first()
    
    if not settings:
        # 如果没有设置记录，创建默认设置
        settings = SiteSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    response = SiteSettingsResponse(
        id=settings.id,
        site_name=settings.site_name,
        site_description=settings.site_description,
        site_keywords=settings.site_keywords,
        page_size=settings.page_size,
        allow_register=settings.allow_register,
        default_public=settings.default_public,
        enable_market=settings.enable_market,
        enable_abtest=settings.enable_abtest,
        max_abtest_prompts=settings.max_abtest_prompts,
        version=settings.version,
        updated_at=settings.updated_at
    )
    
    return success_response(data=response.model_dump())


@router.put("/site-settings", response_model=dict)
async def update_site_settings(
    settings_data: SiteSettingsUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """更新网站设置（管理员）"""
    settings = db.exec(select(SiteSettings)).first()
    
    if not settings:
        # 如果没有设置记录，创建新的
        settings = SiteSettings()
        db.add(settings)
    
    # 更新字段
    if settings_data.site_name is not None:
        settings.site_name = settings_data.site_name
    if settings_data.site_description is not None:
        settings.site_description = settings_data.site_description
    if settings_data.site_keywords is not None:
        settings.site_keywords = settings_data.site_keywords
    if settings_data.page_size is not None:
        settings.page_size = settings_data.page_size
    if settings_data.allow_register is not None:
        settings.allow_register = settings_data.allow_register
    if settings_data.default_public is not None:
        settings.default_public = settings_data.default_public
    if settings_data.enable_market is not None:
        settings.enable_market = settings_data.enable_market
    if settings_data.enable_abtest is not None:
        settings.enable_abtest = settings_data.enable_abtest
    if settings_data.max_abtest_prompts is not None:
        settings.max_abtest_prompts = settings_data.max_abtest_prompts
    
    # 更新时间
    from datetime import datetime
    settings.updated_at = datetime.utcnow()
    
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    response = SiteSettingsResponse(
        id=settings.id,
        site_name=settings.site_name,
        site_description=settings.site_description,
        site_keywords=settings.site_keywords,
        page_size=settings.page_size,
        allow_register=settings.allow_register,
        default_public=settings.default_public,
        enable_market=settings.enable_market,
        enable_abtest=settings.enable_abtest,
        max_abtest_prompts=settings.max_abtest_prompts,
        version=settings.version,
        updated_at=settings.updated_at
    )
    
    return success_response(data=response.model_dump(), message="网站设置更新成功")


# ==================== 模板库管理 ====================

@router.post("/templates")
async def create_template(
    template_data: PromptTemplateCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """创建模板（管理员）"""
    template = PromptTemplate(
        category_id=template_data.category_id,
        title=template_data.title,
        description=template_data.description,
        content=template_data.content,
        variables=template_data.variables,
        example_input=template_data.example_input,
        example_output=template_data.example_output,
        tags=template_data.tags,
        difficulty=template_data.difficulty,
        is_official=True,  # 管理员创建的模板标记为官方
        is_featured=template_data.is_featured if hasattr(template_data, 'is_featured') else False,
        author_id=current_user.id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return success_response(data={"id": template.id}, message="模板创建成功")


@router.put("/templates/{template_id}")
async def update_template(
    template_id: int,
    template_data: PromptTemplateUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """更新模板（管理员）"""
    template = db.get(PromptTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 更新字段
    update_data = template_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return success_response(data={"id": template.id}, message="模板更新成功")


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """删除模板（管理员）"""
    template = db.get(PromptTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 软删除
    template.is_active = False
    db.add(template)
    db.commit()
    
    return success_response(message="模板删除成功")


# ==================== 团队管理 ====================

@router.get("/teams", response_model=dict)
async def get_all_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """获取所有团队列表（管理员）"""
    query = select(Team)
    
    if search:
        query = query.where(Team.name.contains(search))
    
    # 统计总数
    total = len(db.exec(query).all())
    
    # 分页
    teams = db.exec(query.order_by(Team.created_at.desc()).offset(skip).limit(limit)).all()
    
    result = []
    for team in teams:
        # 获取所有者信息
        owner = db.get(User, team.owner_id)
        
        # 统计成员数
        member_count = len(db.exec(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.status == "active"
            )
        ).all())
        
        # 统计 Prompt 数
        prompt_count = len(db.exec(
            select(TeamPrompt).where(TeamPrompt.team_id == team.id)
        ).all())
        
        result.append({
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "owner_id": team.owner_id,
            "owner_username": owner.username if owner else None,
            "is_public": team.is_public,
            "member_count": member_count,
            "prompt_count": prompt_count,
            "created_at": team.created_at.isoformat() if team.created_at else None,
            "updated_at": team.updated_at.isoformat() if team.updated_at else None
        })
    
    return success_response(data={
        "items": result,
        "total": total,
        "skip": skip,
        "limit": limit
    })


@router.get("/teams/{team_id}", response_model=dict)
async def get_team_detail_admin(
    team_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """获取团队详情（管理员）"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    owner = db.get(User, team.owner_id)
    
    # 获取成员列表
    members = db.exec(
        select(TeamMember).where(TeamMember.team_id == team_id)
    ).all()
    
    member_list = []
    for m in members:
        user = db.get(User, m.user_id)
        if user:
            member_list.append({
                "id": m.id,
                "user_id": m.user_id,
                "username": user.username,
                "email": user.email,
                "role": m.role,
                "status": m.status,
                "joined_at": m.joined_at.isoformat() if m.joined_at else None
            })
    
    # 获取 Prompt 列表
    team_prompts = db.exec(
        select(TeamPrompt).where(TeamPrompt.team_id == team_id)
    ).all()
    
    prompt_list = []
    for tp in team_prompts:
        prompt = db.get(Prompt, tp.prompt_id)
        if prompt:
            prompt_list.append({
                "id": tp.id,
                "prompt_id": tp.prompt_id,
                "prompt_title": prompt.title,
                "permission": tp.permission
            })
    
    return success_response(data={
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "owner_id": team.owner_id,
        "owner_username": owner.username if owner else None,
        "is_public": team.is_public,
        "allow_member_invite": team.allow_member_invite,
        "members": member_list,
        "prompts": prompt_list,
        "created_at": team.created_at.isoformat() if team.created_at else None,
        "updated_at": team.updated_at.isoformat() if team.updated_at else None
    })


@router.put("/teams/{team_id}", response_model=dict)
async def update_team_admin(
    team_id: int,
    data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """更新团队（管理员）"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    if "name" in data:
        team.name = data["name"]
    if "description" in data:
        team.description = data["description"]
    if "is_public" in data:
        team.is_public = data["is_public"]
    if "allow_member_invite" in data:
        team.allow_member_invite = data["allow_member_invite"]
    if "owner_id" in data:
        # 转移所有权
        new_owner = db.get(User, data["owner_id"])
        if not new_owner:
            raise HTTPException(status_code=400, detail="新所有者不存在")
        team.owner_id = data["owner_id"]
    
    db.add(team)
    db.commit()
    
    return success_response(message="团队更新成功")


@router.delete("/teams/{team_id}", response_model=dict)
async def delete_team_admin(
    team_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """删除团队（管理员）"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 删除成员
    for m in db.exec(select(TeamMember).where(TeamMember.team_id == team_id)).all():
        db.delete(m)
    
    # 删除 Prompt 关联
    for tp in db.exec(select(TeamPrompt).where(TeamPrompt.team_id == team_id)).all():
        db.delete(tp)
    
    db.delete(team)
    db.commit()
    
    return success_response(message="团队已删除")


@router.delete("/teams/{team_id}/members/{member_id}", response_model=dict)
async def remove_team_member_admin(
    team_id: int,
    member_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """移除团队成员（管理员）"""
    member = db.get(TeamMember, member_id)
    if not member or member.team_id != team_id:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    db.delete(member)
    db.commit()
    
    return success_response(message="成员已移除")

