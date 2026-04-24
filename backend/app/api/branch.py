"""Branch API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.version_control_service import version_control_service

router = APIRouter(prefix="/prompt/{prompt_id}/branches", tags=["branch"])


class BranchCreate(BaseModel):
    name: str
    description: Optional[str] = None
    base_branch_id: Optional[int] = None


class BranchResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_default: bool
    prompt_id: int
    created_by: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=dict)
async def create_branch(
    prompt_id: int,
    branch_data: BranchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建分支"""
    try:
        branch = version_control_service.create_branch(
            db=db,
            prompt_id=prompt_id,
            name=branch_data.name,
            base_branch_id=branch_data.base_branch_id,
            user_id=current_user.id,
            description=branch_data.description
        )
        return {
            "code": 0,
            "data": {
                "id": branch.id,
                "name": branch.name,
                "prompt_id": branch.prompt_id,
                "is_default": branch.is_default,
                "created_at": branch.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=dict)
async def list_branches(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分支列表"""
    branches = version_control_service.get_branches(db, prompt_id)

    # 补充每个分支的提交数量
    branch_list = []
    for b in branches:
        from app.models.commit import PromptCommit
        commit_count = db.query(PromptCommit).filter(
            PromptCommit.branch_id == b.id
        ).count()

        last_commit = db.query(PromptCommit).filter(
            PromptCommit.branch_id == b.id
        ).order_by(PromptCommit.created_at.desc()).first()

        branch_list.append({
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "is_default": b.is_default,
            "commit_count": commit_count,
            "last_commit": {
                "id": last_commit.id,
                "title": last_commit.title,
                "created_at": last_commit.created_at.isoformat()
            } if last_commit else None
        })

    return {"code": 0, "data": branch_list}


@router.get("/{branch_id}", response_model=dict)
async def get_branch(
    prompt_id: int,
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分支详情"""
    branch = version_control_service.get_branch(db, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="分支不存在")

    if branch.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="分支不存在")

    return {
        "code": 0,
        "data": {
            "id": branch.id,
            "name": branch.name,
            "description": branch.description,
            "is_default": branch.is_default,
            "prompt_id": branch.prompt_id
        }
    }


@router.patch("/{branch_id}/switch", response_model=dict)
async def switch_branch(
    prompt_id: int,
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """切换到指定分支，返回该分支最新内容"""
    branch = version_control_service.get_branch(db, branch_id)
    if not branch or branch.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="分支不存在")

    content = version_control_service.get_branch_content(db, branch_id)

    return {
        "code": 0,
        "data": {
            "branch_id": branch_id,
            "branch_name": branch.name,
            "content": content
        }
    }


@router.delete("/{branch_id}", response_model=dict)
async def delete_branch(
    prompt_id: int,
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除分支"""
    try:
        version_control_service.delete_branch(db, branch_id)
        return {"code": 0, "message": "分支已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))