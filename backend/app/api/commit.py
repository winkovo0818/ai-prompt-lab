"""Commit API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.version_control_service import version_control_service

router = APIRouter(prefix="/api/prompt/{prompt_id}/commits", tags=["commit"])


class CommitCreate(BaseModel):
    branch_id: int
    title: str
    content: str
    variables_schema: Optional[dict] = None


class CommitResponse(BaseModel):
    id: int
    branch_id: int
    parent_id: Optional[int]
    title: str
    content: str
    variables_schema: Optional[dict]
    created_by: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=dict)
async def create_commit(
    prompt_id: int,
    commit_data: CommitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建提交（保存新版本）"""
    # 验证分支存在且属于该 prompt
    branch = version_control_service.get_branch(db, commit_data.branch_id)
    if not branch or branch.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="分支不存在")

    commit = version_control_service.create_commit(
        db=db,
        branch_id=commit_data.branch_id,
        user_id=current_user.id,
        title=commit_data.title,
        content=commit_data.content,
        variables_schema=commit_data.variables_schema
    )

    return {
        "code": 0,
        "data": {
            "id": commit.id,
            "branch_id": commit.branch_id,
            "parent_id": commit.parent_id,
            "title": commit.title,
            "created_at": commit.created_at.isoformat()
        }
    }


@router.get("", response_model=dict)
async def list_commits(
    prompt_id: int,
    branch_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分支的提交历史"""
    # 验证分支
    branch = version_control_service.get_branch(db, branch_id)
    if not branch or branch.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="分支不存在")

    result = version_control_service.get_commits(db, branch_id, page, page_size)

    return {
        "code": 0,
        "data": {
            "items": [
                {
                    "id": c.id,
                    "branch_id": c.branch_id,
                    "parent_id": c.parent_id,
                    "title": c.title,
                    "created_by": c.created_by,
                    "created_at": c.created_at.isoformat()
                }
                for c in result['items']
            ],
            "total": result['total'],
            "page": result['page'],
            "page_size": result['page_size']
        }
    }


@router.get("/{commit_id}", response_model=dict)
async def get_commit(
    prompt_id: int,
    commit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取特定提交详情"""
    commit = version_control_service.get_commit(db, commit_id)
    if not commit:
        raise HTTPException(status_code=404, detail="提交不存在")

    # 验证分支属于该 prompt
    branch = version_control_service.get_branch(db, commit.branch_id)
    if not branch or branch.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="提交不存在")

    return {
        "code": 0,
        "data": {
            "id": commit.id,
            "branch_id": commit.branch_id,
            "parent_id": commit.parent_id,
            "title": commit.title,
            "content": commit.content,
            "variables_schema": commit.variables_schema,
            "created_by": commit.created_by,
            "created_at": commit.created_at.isoformat()
        }
    }


@router.post("/revert", response_model=dict)
async def revert_to_commit(
    prompt_id: int,
    branch_id: int = Query(...),
    commit_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """回滚到指定版本"""
    # 验证分支
    branch = version_control_service.get_branch(db, branch_id)
    if not branch or branch.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="分支不存在")

    try:
        new_commit = version_control_service.revert_to_commit(
            db=db,
            branch_id=branch_id,
            target_commit_id=commit_id,
            user_id=current_user.id
        )
        return {
            "code": 0,
            "data": {
                "new_commit_id": new_commit.id,
                "title": new_commit.title
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))