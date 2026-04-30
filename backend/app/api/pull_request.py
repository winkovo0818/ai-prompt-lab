"""Pull Request API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.pull_request_service import pull_request_service
from app.services.version_control_service import version_control_service

router = APIRouter(prefix="/api/prompt/{prompt_id}/pull-requests", tags=["pull_request"])


class PRCreate(BaseModel):
    source_branch_id: int
    target_branch_id: int
    title: str
    description: Optional[str] = None


class PRReviewRequest(BaseModel):
    reviewer_id: Optional[int] = None


@router.post("", response_model=dict)
async def create_pull_request(
    prompt_id: int,
    pr_data: PRCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建 Pull Request"""
    try:
        pr = pull_request_service.create_pr(
            db=db,
            prompt_id=prompt_id,
            source_branch_id=pr_data.source_branch_id,
            target_branch_id=pr_data.target_branch_id,
            title=pr_data.title,
            author_id=current_user.id,
            description=pr_data.description
        )
        return {
            "code": 0,
            "data": {
                "id": pr.id,
                "title": pr.title,
                "status": pr.status,
                "source_branch_id": pr.source_branch_id,
                "target_branch_id": pr.target_branch_id,
                "created_at": pr.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=dict)
async def list_pull_requests(
    prompt_id: int,
    status: Optional[str] = Query(None, description="过滤状态: open/merged/closed"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 PR 列表"""
    result = pull_request_service.get_prs(db, prompt_id, status, page, page_size)

    items = []
    for pr in result['items']:
        # 获取分支名称
        source_branch = version_control_service.get_branch(db, pr.source_branch_id)
        target_branch = version_control_service.get_branch(db, pr.target_branch_id)

        items.append({
            "id": pr.id,
            "title": pr.title,
            "description": pr.description,
            "status": pr.status,
            "author_id": pr.author_id,
            "source_branch": {
                "id": source_branch.id if source_branch else None,
                "name": source_branch.name if source_branch else None
            },
            "target_branch": {
                "id": target_branch.id if target_branch else None,
                "name": target_branch.name if target_branch else None
            },
            "created_at": pr.created_at.isoformat(),
            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None
        })

    return {
        "code": 0,
        "data": {
            "items": items,
            "total": result['total'],
            "page": result['page'],
            "page_size": result['page_size']
        }
    }


@router.get("/{pr_id}", response_model=dict)
async def get_pull_request(
    prompt_id: int,
    pr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 PR 详情"""
    pr = pull_request_service.get_pr(db, pr_id)
    if not pr or pr.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="PR 不存在")

    # 检查能否合并
    can_merge = pull_request_service.can_merge(db, pr_id)

    # 获取分支信息
    source_branch = version_control_service.get_branch(db, pr.source_branch_id)
    target_branch = version_control_service.get_branch(db, pr.target_branch_id)

    return {
        "code": 0,
        "data": {
            "id": pr.id,
            "title": pr.title,
            "description": pr.description,
            "status": pr.status,
            "author_id": pr.author_id,
            "reviewer_id": pr.reviewer_id,
            "source_branch": {
                "id": source_branch.id if source_branch else None,
                "name": source_branch.name if source_branch else None
            },
            "target_branch": {
                "id": target_branch.id if target_branch else None,
                "name": target_branch.name if target_branch else None
            },
            "can_merge": can_merge['can_merge'],
            "created_at": pr.created_at.isoformat(),
            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None
        }
    }


@router.post("/{pr_id}/merge", response_model=dict)
async def merge_pull_request(
    prompt_id: int,
    pr_id: int,
    merge_method: str = Query("squash", description="合并方式: squash 或 merge"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """合并 Pull Request"""
    pr = pull_request_service.get_pr(db, pr_id)
    if not pr or pr.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="PR 不存在")

    try:
        result = pull_request_service.merge(
            db=db,
            pr_id=pr_id,
            user_id=current_user.id,
            merge_method=merge_method
        )
        return {
            "code": 0,
            "data": {
                "merged": True,
                "new_commit_id": result['new_commit_id']
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pr_id}/close", response_model=dict)
async def close_pull_request(
    prompt_id: int,
    pr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """关闭 Pull Request"""
    pr = pull_request_service.get_pr(db, pr_id)
    if not pr or pr.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="PR 不存在")

    try:
        pr = pull_request_service.close_pr(db, pr_id, current_user.id)
        return {
            "code": 0,
            "data": {
                "id": pr.id,
                "status": pr.status
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{pr_id}/reviewers", response_model=dict)
async def update_pr_reviewers(
    prompt_id: int,
    pr_id: int,
    review_data: PRReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新 PR 审核人"""
    pr = pull_request_service.get_pr(db, pr_id)
    if not pr or pr.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="PR 不存在")

    pr = pull_request_service.update_pr_reviewers(
        db=db,
        pr_id=pr_id,
        reviewer_id=review_data.reviewer_id
    )

    return {
        "code": 0,
        "data": {
            "id": pr.id,
            "reviewer_id": pr.reviewer_id
        }
    }