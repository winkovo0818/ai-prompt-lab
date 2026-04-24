"""
团队工作区 API
支持团队管理、成员管理、Prompt 共享
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, or_

from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.prompt import Prompt
from ..models.team import (
    Team, TeamMember, TeamPrompt, TeamInvite,
    TeamCreate, TeamUpdate, TeamMemberAdd, TeamMemberUpdate,
    TeamPromptShare, TeamInviteCreate,
    TeamResponse, TeamMemberResponse, TeamPromptResponse
)

router = APIRouter(prefix="/api/team", tags=["团队工作区"])


# ==================== 团队管理 ====================

@router.get("/list")
async def get_my_teams(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的团队列表"""
    # 查询我创建的或加入的团队
    member_teams = db.exec(
        select(TeamMember.team_id).where(
            TeamMember.user_id == current_user.id,
            TeamMember.status == "active"
        )
    ).all()
    
    owned_teams = db.exec(
        select(Team.id).where(Team.owner_id == current_user.id)
    ).all()
    
    team_ids = list(set(member_teams + owned_teams))
    
    if not team_ids:
        return {"code": 0, "data": []}
    
    teams = db.exec(select(Team).where(Team.id.in_(team_ids))).all()
    
    result = []
    for team in teams:
        # 统计成员数
        member_count = db.exec(
            select(func.count(TeamMember.id)).where(
                TeamMember.team_id == team.id,
                TeamMember.status == "active"
            )
        ).first() or 0
        
        # 统计 Prompt 数
        prompt_count = db.exec(
            select(func.count(TeamPrompt.id)).where(TeamPrompt.team_id == team.id)
        ).first() or 0
        
        # 获取我的角色
        my_role = "owner" if team.owner_id == current_user.id else None
        if not my_role:
            member = db.exec(
                select(TeamMember).where(
                    TeamMember.team_id == team.id,
                    TeamMember.user_id == current_user.id,
                    TeamMember.status == "active"
                )
            ).first()
            if member:
                my_role = member.role
        
        result.append(TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            avatar_url=team.avatar_url,
            owner_id=team.owner_id,
            is_public=team.is_public,
            allow_member_invite=team.allow_member_invite,
            member_count=member_count,
            prompt_count=prompt_count,
            my_role=my_role,
            created_at=team.created_at,
            updated_at=team.updated_at
        ).model_dump())
    
    return {"code": 0, "data": result}


@router.post("")
async def create_team(
    data: TeamCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建团队"""
    team = Team(
        name=data.name,
        description=data.description,
        avatar_url=data.avatar_url,
        owner_id=current_user.id,
        is_public=data.is_public,
        allow_member_invite=data.allow_member_invite
    )
    
    db.add(team)
    db.commit()
    db.refresh(team)
    
    # 自动将创建者添加为成员（owner角色）
    member = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role="owner",
        status="active",
        joined_at=datetime.utcnow()
    )
    db.add(member)
    db.commit()
    
    return {
        "code": 0,
        "data": {"id": team.id, "name": team.name},
        "message": "团队创建成功"
    }


@router.get("/{team_id}")
async def get_team(
    team_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取团队详情"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 检查权限
    if not _can_view_team(team, current_user, db):
        raise HTTPException(status_code=403, detail="无权限查看此团队")
    
    # 统计
    member_count = db.exec(
        select(func.count(TeamMember.id)).where(
            TeamMember.team_id == team.id,
            TeamMember.status == "active"
        )
    ).first() or 0
    
    prompt_count = db.exec(
        select(func.count(TeamPrompt.id)).where(TeamPrompt.team_id == team.id)
    ).first() or 0
    
    my_role = _get_user_role(team, current_user, db)
    
    return {
        "code": 0,
        "data": TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            avatar_url=team.avatar_url,
            owner_id=team.owner_id,
            is_public=team.is_public,
            allow_member_invite=team.allow_member_invite,
            member_count=member_count,
            prompt_count=prompt_count,
            my_role=my_role,
            created_at=team.created_at,
            updated_at=team.updated_at
        ).model_dump()
    }


@router.put("/{team_id}")
async def update_team(
    team_id: int,
    data: TeamUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新团队"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 只有所有者可以更新
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有团队所有者可以修改设置")
    
    if data.name is not None:
        team.name = data.name
    if data.description is not None:
        team.description = data.description
    if data.avatar_url is not None:
        team.avatar_url = data.avatar_url
    if data.is_public is not None:
        team.is_public = data.is_public
    if data.allow_member_invite is not None:
        team.allow_member_invite = data.allow_member_invite
    
    team.updated_at = datetime.utcnow()
    
    db.add(team)
    db.commit()
    
    return {"code": 0, "message": "更新成功"}


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除团队"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有团队所有者可以删除团队")
    
    # 删除相关数据
    db.exec(select(TeamMember).where(TeamMember.team_id == team_id))
    for m in db.exec(select(TeamMember).where(TeamMember.team_id == team_id)).all():
        db.delete(m)
    
    for p in db.exec(select(TeamPrompt).where(TeamPrompt.team_id == team_id)).all():
        db.delete(p)
    
    for i in db.exec(select(TeamInvite).where(TeamInvite.team_id == team_id)).all():
        db.delete(i)
    
    db.delete(team)
    db.commit()
    
    return {"code": 0, "message": "团队已删除"}


# ==================== 成员管理 ====================

@router.get("/{team_id}/members")
async def get_team_members(
    team_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取团队成员列表"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    if not _can_view_team(team, current_user, db):
        raise HTTPException(status_code=403, detail="无权限查看")
    
    members = db.exec(
        select(TeamMember).where(TeamMember.team_id == team_id)
    ).all()
    
    result = []
    for member in members:
        user = db.get(User, member.user_id)
        if not user:
            continue
        
        invited_by_username = None
        if member.invited_by:
            inviter = db.get(User, member.invited_by)
            if inviter:
                invited_by_username = inviter.username
        
        result.append(TeamMemberResponse(
            id=member.id,
            team_id=member.team_id,
            user_id=member.user_id,
            username=user.username,
            email=user.email,
            avatar_url=user.avatar_url,
            role=member.role,
            status=member.status,
            joined_at=member.joined_at,
            invited_by_username=invited_by_username
        ).model_dump())
    
    return {"code": 0, "data": result}


@router.post("/{team_id}/members")
async def add_team_member(
    team_id: int,
    data: TeamMemberAdd,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """添加团队成员"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 检查权限
    my_role = _get_user_role(team, current_user, db)
    if my_role not in ["owner", "editor"]:
        if not (team.allow_member_invite and my_role == "viewer"):
            raise HTTPException(status_code=403, detail="无权限添加成员")
    
    # 不能添加比自己更高的角色
    if data.role == "owner" and my_role != "owner":
        raise HTTPException(status_code=403, detail="无权限设置此角色")
    
    # 查找用户
    target_user = None
    if data.user_id:
        target_user = db.get(User, data.user_id)
    elif data.email:
        target_user = db.exec(
            select(User).where(User.email == data.email)
        ).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查是否已是成员
    existing = db.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == target_user.id
        )
    ).first()
    
    if existing:
        if existing.status == "active":
            raise HTTPException(status_code=400, detail="用户已是团队成员")
        # 重新激活
        existing.status = "active"
        existing.role = data.role
        existing.joined_at = datetime.utcnow()
        db.add(existing)
        db.commit()
    else:
        member = TeamMember(
            team_id=team_id,
            user_id=target_user.id,
            role=data.role,
            invited_by=current_user.id,
            status="active",
            joined_at=datetime.utcnow()
        )
        db.add(member)
        db.commit()
    
    return {"code": 0, "message": "成员添加成功"}


@router.put("/{team_id}/members/{member_id}")
async def update_team_member(
    team_id: int,
    member_id: int,
    data: TeamMemberUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新成员角色"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    member = db.get(TeamMember, member_id)
    if not member or member.team_id != team_id:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    my_role = _get_user_role(team, current_user, db)
    if my_role != "owner":
        raise HTTPException(status_code=403, detail="只有所有者可以修改角色")
    
    # 不能修改自己的角色
    if member.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")
    
    member.role = data.role
    db.add(member)
    db.commit()
    
    return {"code": 0, "message": "角色更新成功"}


@router.delete("/{team_id}/members/{member_id}")
async def remove_team_member(
    team_id: int,
    member_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """移除成员"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    member = db.get(TeamMember, member_id)
    if not member or member.team_id != team_id:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    my_role = _get_user_role(team, current_user, db)
    
    # 所有者可以移除任何人，成员可以自己退出
    if my_role != "owner" and member.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限移除此成员")
    
    # 所有者不能移除自己
    if member.user_id == team.owner_id:
        raise HTTPException(status_code=400, detail="所有者不能退出团队")
    
    member.status = "removed"
    db.add(member)
    db.commit()
    
    return {"code": 0, "message": "成员已移除"}


# ==================== 团队 Prompt 管理 ====================

@router.get("/{team_id}/prompts")
async def get_team_prompts(
    team_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取团队 Prompt 列表"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    if not _can_view_team(team, current_user, db):
        raise HTTPException(status_code=403, detail="无权限查看")
    
    # 查询团队 Prompt
    statement = select(TeamPrompt).where(
        TeamPrompt.team_id == team_id
    ).offset(skip).limit(limit)
    
    team_prompts = db.exec(statement).all()
    
    result = []
    for tp in team_prompts:
        prompt = db.get(Prompt, tp.prompt_id)
        if not prompt:
            continue
        
        sharer = db.get(User, tp.shared_by)
        
        result.append(TeamPromptResponse(
            id=tp.id,
            team_id=tp.team_id,
            prompt_id=tp.prompt_id,
            prompt_title=prompt.title,
            prompt_description=prompt.description,
            permission=tp.permission,
            shared_by_username=sharer.username if sharer else "Unknown",
            created_at=tp.created_at
        ).model_dump())
    
    # 统计总数
    total = db.exec(
        select(func.count(TeamPrompt.id)).where(TeamPrompt.team_id == team_id)
    ).first() or 0
    
    return {
        "code": 0,
        "data": {
            "items": result,
            "total": total
        }
    }


@router.post("/{team_id}/prompts")
async def share_prompt_to_team(
    team_id: int,
    data: TeamPromptShare,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """共享 Prompt 到团队"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 检查权限（需要是编辑者或所有者）
    my_role = _get_user_role(team, current_user, db)
    if my_role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="无权限共享 Prompt")
    
    # 检查 Prompt 是否存在且属于当前用户
    prompt = db.get(Prompt, data.prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt 不存在")
    
    if prompt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能共享自己的 Prompt")
    
    # 检查是否已共享
    existing = db.exec(
        select(TeamPrompt).where(
            TeamPrompt.team_id == team_id,
            TeamPrompt.prompt_id == data.prompt_id
        )
    ).first()
    
    if existing:
        existing.permission = data.permission
        db.add(existing)
        db.commit()
        return {"code": 0, "message": "共享权限已更新"}
    
    team_prompt = TeamPrompt(
        team_id=team_id,
        prompt_id=data.prompt_id,
        shared_by=current_user.id,
        permission=data.permission
    )
    
    db.add(team_prompt)
    db.commit()
    
    return {"code": 0, "message": "Prompt 已共享到团队"}


@router.delete("/{team_id}/prompts/{team_prompt_id}")
async def remove_prompt_from_team(
    team_id: int,
    team_prompt_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """从团队移除 Prompt"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    team_prompt = db.get(TeamPrompt, team_prompt_id)
    if not team_prompt or team_prompt.team_id != team_id:
        raise HTTPException(status_code=404, detail="团队 Prompt 不存在")
    
    my_role = _get_user_role(team, current_user, db)
    
    # 所有者、编辑者、或分享者可以移除
    if my_role not in ["owner", "editor"] and team_prompt.shared_by != current_user.id:
        raise HTTPException(status_code=403, detail="无权限移除")
    
    db.delete(team_prompt)
    db.commit()
    
    return {"code": 0, "message": "已从团队移除"}


# ==================== 邀请链接 ====================

@router.post("/{team_id}/invites")
async def create_invite_link(
    team_id: int,
    data: TeamInviteCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建邀请链接"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    my_role = _get_user_role(team, current_user, db)
    if my_role not in ["owner", "editor"]:
        if not (team.allow_member_invite and my_role == "viewer"):
            raise HTTPException(status_code=403, detail="无权限创建邀请")
    
    # 生成邀请码
    invite_code = secrets.token_urlsafe(16)
    
    expires_at = None
    if data.expires_hours:
        expires_at = datetime.utcnow() + timedelta(hours=data.expires_hours)
    
    invite = TeamInvite(
        team_id=team_id,
        invite_code=invite_code,
        role=data.role,
        created_by=current_user.id,
        expires_at=expires_at,
        max_uses=data.max_uses
    )
    
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    return {
        "code": 0,
        "data": {
            "invite_code": invite_code,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "max_uses": data.max_uses
        }
    }


@router.post("/join/{invite_code}")
async def join_team_by_invite(
    invite_code: str,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """通过邀请码加入团队"""
    invite = db.exec(
        select(TeamInvite).where(
            TeamInvite.invite_code == invite_code,
            TeamInvite.is_active == True
        )
    ).first()
    
    if not invite:
        raise HTTPException(status_code=404, detail="邀请链接无效")
    
    # 检查是否过期
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="邀请链接已过期")
    
    # 检查使用次数
    if invite.used_count >= invite.max_uses:
        raise HTTPException(status_code=400, detail="邀请链接已达到最大使用次数")
    
    team = db.get(Team, invite.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 检查是否已是成员
    existing = db.exec(
        select(TeamMember).where(
            TeamMember.team_id == invite.team_id,
            TeamMember.user_id == current_user.id,
            TeamMember.status == "active"
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="你已是团队成员")
    
    # 加入团队
    member = TeamMember(
        team_id=invite.team_id,
        user_id=current_user.id,
        role=invite.role,
        invited_by=invite.created_by,
        status="active",
        joined_at=datetime.utcnow()
    )
    
    db.add(member)
    
    # 更新使用次数
    invite.used_count += 1
    db.add(invite)
    
    db.commit()
    
    return {
        "code": 0,
        "data": {
            "team_id": team.id,
            "team_name": team.name
        },
        "message": f"已成功加入团队 {team.name}"
    }


# ==================== 辅助函数 ====================

def _can_view_team(team: Team, user: User, db: Session) -> bool:
    """检查用户是否可以查看团队"""
    if team.is_public:
        return True
    if team.owner_id == user.id:
        return True
    
    member = db.exec(
        select(TeamMember).where(
            TeamMember.team_id == team.id,
            TeamMember.user_id == user.id,
            TeamMember.status == "active"
        )
    ).first()
    
    return member is not None


def _get_user_role(team: Team, user: User, db: Session) -> Optional[str]:
    """获取用户在团队中的角色"""
    if team.owner_id == user.id:
        return "owner"
    
    member = db.exec(
        select(TeamMember).where(
            TeamMember.team_id == team.id,
            TeamMember.user_id == user.id,
            TeamMember.status == "active"
        )
    ).first()
    
    return member.role if member else None
