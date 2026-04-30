"""Diff API - 版本对比"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.diff_service import diff_service
from app.services.version_control_service import version_control_service

router = APIRouter(prefix="/api/prompt/{prompt_id}/diff", tags=["diff"])


@router.get("", response_model=dict)
async def compute_diff(
    prompt_id: int,
    from_commit: int = Query(..., description="起始提交 ID"),
    to_commit: int = Query(..., description="目标提交 ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """计算两个版本之间的差异"""
    # 获取两个提交
    from_commit_obj = version_control_service.get_commit(db, from_commit)
    to_commit_obj = version_control_service.get_commit(db, to_commit)

    if not from_commit_obj:
        raise HTTPException(status_code=404, detail=f"起始提交 {from_commit} 不存在")
    if not to_commit_obj:
        raise HTTPException(status_code=404, detail=f"目标提交 {to_commit} 不存在")

    # 验证两个提交属于同一个 prompt
    from_branch = version_control_service.get_branch(db, from_commit_obj.branch_id)
    to_branch = version_control_service.get_branch(db, to_commit_obj.branch_id)

    if from_branch.prompt_id != prompt_id or to_branch.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="提交不属于该 Prompt")

    # 计算差异
    diff_result = diff_service.compute_diff(
        from_commit_obj.content,
        to_commit_obj.content
    )

    return {
        "code": 0,
        "data": {
            "from": {
                "commit_id": from_commit_obj.id,
                "title": from_commit_obj.title,
                "content": from_commit_obj.content,
                "branch_id": from_commit_obj.branch_id,
                "created_at": from_commit_obj.created_at.isoformat()
            },
            "to": {
                "commit_id": to_commit_obj.id,
                "title": to_commit_obj.title,
                "content": to_commit_obj.content,
                "branch_id": to_commit_obj.branch_id,
                "created_at": to_commit_obj.created_at.isoformat()
            },
            "diff": diff_result
        }
    }


@router.get("/unified", response_model=dict)
async def get_unified_diff(
    prompt_id: int,
    from_commit: int = Query(...),
    to_commit: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 unified diff 格式"""
    from_commit_obj = version_control_service.get_commit(db, from_commit)
    to_commit_obj = version_control_service.get_commit(db, to_commit)

    if not from_commit_obj or not to_commit_obj:
        raise HTTPException(status_code=404, detail="提交不存在")

    unified = diff_service.compute_unified_diff(
        from_commit_obj.content,
        to_commit_obj.content,
        fromfile=f"commit-{from_commit}",
        tofile=f"commit-{to_commit}"
    )

    return {
        "code": 0,
        "data": {
            "unified_diff": unified
        }
    }