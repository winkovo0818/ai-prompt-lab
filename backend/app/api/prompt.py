from typing import List, Optional, Tuple
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_
from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.prompt import (
    Prompt, PromptCreate, PromptUpdate,
    PromptResponse, PromptListItem, UserPromptFavorite
)
from ..models.prompt_version import PromptVersion, PromptVersionResponse
from ..models.team import TeamPrompt, TeamMember
from ..utils.response import success_response, error_response

router = APIRouter(prefix="/api/prompt", tags=["Prompt管理"])


def check_prompt_access(prompt_id: int, current_user: User, db: Session, require_edit: bool = False) -> Tuple[Prompt, Optional[dict]]:
    """
    检查用户是否有权访问指�?Prompt（可复用的权限检查函数）

    Args:
        prompt_id: Prompt ID
        current_user: 当前用户
        db: 数据库会�?        require_edit: 是否需要编辑权�?
    Returns:
        (prompt, team_info) - prompt 对象和团队信息（有的话）

    Raises:
        HTTPException - 无权访问时抛�?    """
    prompt = db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt 不存�?)

    team_permission = None
    team_info = None

    # 检查访问权限：所有者、公开、或团队共享
    if prompt.user_id != current_user.id and not prompt.is_public:
        user_teams = db.exec(
            select(TeamMember).where(
                TeamMember.user_id == current_user.id
            )
        ).all()

        team_ids = [tm.team_id for tm in user_teams]

        if team_ids:
            team_prompt = db.exec(
                select(TeamPrompt).where(
                    TeamPrompt.prompt_id == prompt_id,
                    TeamPrompt.team_id.in_(team_ids)
                )
            ).first()

            if team_prompt:
                team_permission = team_prompt.permission
                team = db.get(Team, team_prompt.team_id)
                team_info = {
                    "team_id": team_prompt.team_id,
                    "team_name": team.name if team else None,
                    "permission": team_prompt.permission
                }

        if not team_permission:
            raise HTTPException(status_code=403, detail="无权访问�?Prompt")

    # 如果需要编辑权�?    if require_edit and prompt.user_id != current_user.id and team_permission != "edit":
        if not (current_user.role == "admin"):
            raise HTTPException(status_code=403, detail="无权编辑�?Prompt")

    return prompt, team_info


@router.post("", response_model=dict)
async def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """创建新的 Prompt"""
    
    # 创建 Prompt
    new_prompt = Prompt(
        user_id=current_user.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        tags=prompt_data.tags or [],
        is_public=prompt_data.is_public,
        version=1
    )
    
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    
    # 创建初始版本
    version = PromptVersion(
        prompt_id=new_prompt.id,
        version=1,
        title=new_prompt.title,
        content=new_prompt.content,
        description=new_prompt.description,
        change_summary="初始版本"
    )
    
    db.add(version)
    db.commit()
    
    response = PromptResponse(
        id=new_prompt.id,
        user_id=new_prompt.user_id,
        title=new_prompt.title,
        content=new_prompt.content,
        description=new_prompt.description,
        tags=new_prompt.tags,
        is_favorite=False,  # 新创建的 Prompt 默认未收�?        is_public=new_prompt.is_public,
        version=new_prompt.version,
        created_at=new_prompt.created_at,
        updated_at=new_prompt.updated_at
    )
    
    return success_response(data=response.model_dump(), message="Prompt 创建成功")


@router.get("/list", response_model=dict)
async def get_prompt_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    tags: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    is_public: Optional[bool] = None,
    include_team: Optional[bool] = Query(True, description="是否包含团队共享�?Prompt"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取 Prompt 列表"""
    
    # 获取用户所属团队的共享 Prompt IDs
    team_prompt_ids = set()
    team_prompt_info = {}  # prompt_id -> {team_name, permission}
    
    if include_team:
        # 获取用户加入的团�?        user_teams = db.exec(
            select(TeamMember).where(
                TeamMember.user_id == current_user.id
            )
        ).all()
        
        team_ids = [tm.team_id for tm in user_teams]
        
        if team_ids:
            # 获取这些团队共享�?Prompt
            from ..models.team import Team
            team_prompts = db.exec(
                select(TeamPrompt).where(TeamPrompt.team_id.in_(team_ids))
            ).all()
            
            for tp in team_prompts:
                # 排除自己创建�?Prompt（避免重复）
                prompt = db.get(Prompt, tp.prompt_id)
                if prompt and prompt.user_id != current_user.id:
                    team_prompt_ids.add(tp.prompt_id)
                    team = db.get(Team, tp.team_id)
                    team_prompt_info[tp.prompt_id] = {
                        "team_id": tp.team_id,
                        "team_name": team.name if team else None,
                        "permission": tp.permission
                    }
    
    # 构建查询 - 包含自己的、公开的、团队共享的
    if team_prompt_ids:
        statement = select(Prompt).where(
            or_(
                Prompt.user_id == current_user.id,
                Prompt.is_public == True,
                Prompt.id.in_(team_prompt_ids)
            )
        )
    else:
        statement = select(Prompt).where(
            or_(
                Prompt.user_id == current_user.id,
                Prompt.is_public == True
            )
        )
    
    # 搜索过滤
    if search:
        statement = statement.where(
            or_(
                Prompt.title.contains(search),
                Prompt.description.contains(search)
            )
        )
    
    # 标签过滤（简化处理）
    # 实际项目中可能需要更复杂�?JSON 查询
    
    # 收藏过滤
    if is_favorite is not None:
        # 使用关联表过滤收�?        if is_favorite:
            # 只显示当前用户收藏的
            favorite_statement = select(UserPromptFavorite.prompt_id).where(
                UserPromptFavorite.user_id == current_user.id
            )
            favorite_ids = db.exec(favorite_statement).all()
            statement = statement.where(Prompt.id.in_(favorite_ids))
        else:
            # 只显示未收藏�?            favorite_statement = select(UserPromptFavorite.prompt_id).where(
                UserPromptFavorite.user_id == current_user.id
            )
            favorite_ids = db.exec(favorite_statement).all()
            if favorite_ids:
                statement = statement.where(~Prompt.id.in_(favorite_ids))
    
    # 公开状态过�?    if is_public is not None:
        statement = statement.where(Prompt.is_public == is_public)
    
    # 排序
    statement = statement.order_by(Prompt.updated_at.desc())

    # 获取总数
    from sqlmodel import func
    count_statement = select(func.count()).select_from(statement)
    total_count = db.exec(count_statement).one()

    # 分页
    statement = statement.offset(skip).limit(limit)
    prompts = db.exec(statement).all()

    # 获取当前用户的所有收�?    favorite_statement = select(UserPromptFavorite.prompt_id).where(
        UserPromptFavorite.user_id == current_user.id
    )
    favorite_ids = set(db.exec(favorite_statement).all())

    # 转换为列表项
    items = []
    for prompt in prompts:
        item_data = {
            "id": prompt.id,
            "title": prompt.title,
            "description": prompt.description,
            "tags": prompt.tags,
            "is_favorite": prompt.id in favorite_ids,
            "is_public": prompt.is_public,
            "is_owner": prompt.user_id == current_user.id,
            "version": prompt.version,
            "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
            "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None,
            # 团队共享信息
            "team_shared": prompt.id in team_prompt_info,
            "team_info": team_prompt_info.get(prompt.id)
        }
        items.append(item_data)
    
    return success_response(data={
        "items": items,
        "total": total_count,
        "skip": skip,
        "limit": limit
    })


@router.get("/{prompt_id}", response_model=dict)
async def get_prompt_detail(
    prompt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取 Prompt 详情"""
    
    prompt = db.get(Prompt, prompt_id)
    
    if not prompt:
        return error_response(code=2001, message="Prompt 不存�?)
    
    # 检查团队共享权�?    team_permission = None
    team_info = None
    
    if prompt.user_id != current_user.id and not prompt.is_public:
        # 检查是否通过团队共享获得权限
        from ..models.team import Team
        user_teams = db.exec(
            select(TeamMember).where(
                TeamMember.user_id == current_user.id
            )
        ).all()
        
        team_ids = [tm.team_id for tm in user_teams]
        
        if team_ids:
            team_prompt = db.exec(
                select(TeamPrompt).where(
                    TeamPrompt.prompt_id == prompt_id,
                    TeamPrompt.team_id.in_(team_ids)
                )
            ).first()
            
            if team_prompt:
                team_permission = team_prompt.permission
                team = db.get(Team, team_prompt.team_id)
                team_info = {
                    "team_id": team_prompt.team_id,
                    "team_name": team.name if team else None,
                    "permission": team_prompt.permission
                }
        
        if not team_permission:
            return error_response(code=2002, message="无权访问�?Prompt")
    
    # 检查当前用户是否已收藏
    favorite_statement = select(UserPromptFavorite).where(
        UserPromptFavorite.user_id == current_user.id,
        UserPromptFavorite.prompt_id == prompt_id
    )
    is_favorite = db.exec(favorite_statement).first() is not None
    
    # 确定编辑权限
    can_edit = prompt.user_id == current_user.id or team_permission == "edit"
    
    response_data = {
        "id": prompt.id,
        "user_id": prompt.user_id,
        "title": prompt.title,
        "content": prompt.content,
        "description": prompt.description,
        "tags": prompt.tags,
        "is_favorite": is_favorite,
        "is_public": prompt.is_public,
        "version": prompt.version,
        "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
        "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None,
        "is_owner": prompt.user_id == current_user.id,
        "can_edit": can_edit,
        "team_shared": team_info is not None,
        "team_info": team_info
    }
    
    return success_response(data=response_data)


@router.put("/{prompt_id}", response_model=dict)
async def update_prompt(
    prompt_id: int,
    prompt_data: PromptUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """更新 Prompt"""
    
    try:
        prompt = db.get(Prompt, prompt_id)
        
        if not prompt:
            return error_response(code=2001, message="Prompt 不存�?)
        
        # 权限检�?- 支持团队共享编辑权限
        can_edit = prompt.user_id == current_user.id
        
        if not can_edit:
            # 检查是否有团队编辑权限
            user_teams = db.exec(
                select(TeamMember).where(
                    TeamMember.user_id == current_user.id
                )
            ).all()
            
            team_ids = [tm.team_id for tm in user_teams]
            
            if team_ids:
                team_prompt = db.exec(
                    select(TeamPrompt).where(
                        TeamPrompt.prompt_id == prompt_id,
                        TeamPrompt.team_id.in_(team_ids),
                        TeamPrompt.permission == "edit"
                    )
                ).first()
                
                if team_prompt:
                    can_edit = True
        
        if not can_edit:
            return error_response(code=2003, message="无权修改�?Prompt")
        
        # 更新字段
        content_changed = False
        if prompt_data.content and prompt_data.content != prompt.content:
            content_changed = True
        
        # 更新字段
        if prompt_data.title is not None:
            prompt.title = prompt_data.title
        if prompt_data.content is not None:
            prompt.content = prompt_data.content
        if prompt_data.description is not None:
            prompt.description = prompt_data.description
        if prompt_data.tags is not None:
            prompt.tags = prompt_data.tags
        if prompt_data.is_public is not None:
            prompt.is_public = prompt_data.is_public
        
        prompt.updated_at = datetime.utcnow()
        
        # 如果内容有修改，创建新版�?        if content_changed:
            prompt.version += 1
            
            version = PromptVersion(
                prompt_id=prompt.id,
                version=prompt.version,
                title=prompt.title,
                content=prompt.content,
                description=prompt.description,
                change_summary="内容更新"
            )
            db.add(version)
        
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        # 检查当前用户是否已收藏
        favorite_statement = select(UserPromptFavorite).where(
            UserPromptFavorite.user_id == current_user.id,
            UserPromptFavorite.prompt_id == prompt_id
        )
        is_favorite = db.exec(favorite_statement).first() is not None
        
        response = PromptResponse(
            id=prompt.id,
            user_id=prompt.user_id,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            tags=prompt.tags,
            is_favorite=is_favorite,
            is_public=prompt.is_public,
            version=prompt.version,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at
        )
        
        return success_response(data=response.model_dump(), message="Prompt 更新成功")
    
    except Exception as e:
        db.rollback()
        return error_response(code=2004, message=f"更新失败: {str(e)}")


@router.delete("/{prompt_id}", response_model=dict)
async def delete_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """删除 Prompt"""
    
    prompt = db.get(Prompt, prompt_id)
    
    if not prompt:
        return error_response(code=2001, message="Prompt 不存�?)
    
    # 权限检�?    if prompt.user_id != current_user.id:
        return error_response(code=2003, message="无权删除�?Prompt")
    
    db.delete(prompt)
    db.commit()
    
    return success_response(message="Prompt 删除成功")


@router.get("/{prompt_id}/versions", response_model=dict)
async def get_prompt_versions(
    prompt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取 Prompt 的版本历�?""
    
    prompt = db.get(Prompt, prompt_id)
    
    if not prompt:
        return error_response(code=2001, message="Prompt 不存�?)
    
    # 权限检�?    if prompt.user_id != current_user.id and not prompt.is_public:
        return error_response(code=2002, message="无权访问�?Prompt")
    
    # 获取版本列表
    statement = select(PromptVersion).where(
        PromptVersion.prompt_id == prompt_id
    ).order_by(PromptVersion.version.desc())
    
    versions = db.exec(statement).all()
    
    version_list = []
    for version in versions:
        version_data = PromptVersionResponse(
            id=version.id,
            prompt_id=version.prompt_id,
            version=version.version,
            title=version.title,
            content=version.content,
            description=version.description,
            change_summary=version.change_summary,
            created_at=version.created_at
        )
        version_list.append(version_data.model_dump())
    
    return success_response(data=version_list)


@router.post("/{prompt_id}/favorite", response_model=dict)
async def toggle_favorite(
    prompt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """切换收藏状�?""
    
    # 检�?Prompt 是否存在
    prompt = db.get(Prompt, prompt_id)
    if not prompt:
        return error_response(code=2001, message="Prompt 不存�?)
    
    # 检查当前用户是否已收藏
    statement = select(UserPromptFavorite).where(
        UserPromptFavorite.user_id == current_user.id,
        UserPromptFavorite.prompt_id == prompt_id
    )
    favorite = db.exec(statement).first()
    
    if favorite:
        # 取消收藏
        db.delete(favorite)
        db.commit()
        return success_response(
            data={"is_favorite": False},
            message="已取消收�?
        )
    else:
        # 添加收藏
        favorite = UserPromptFavorite(
            user_id=current_user.id,
            prompt_id=prompt_id
        )
        db.add(favorite)
        db.commit()
        return success_response(
            data={"is_favorite": True},
            message="已收�?
        )

