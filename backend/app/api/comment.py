"""
Prompt 评论 API
支持评论、@提及用户、版本评审
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, desc

from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.comment import (
    PromptComment, PromptCommentCreate, 
    PromptCommentUpdate, PromptCommentResponse
)
from ..models.prompt import Prompt

router = APIRouter(prefix="/api/prompt", tags=["Prompt评论"])


@router.get("/{prompt_id}/comments")
async def get_comments(
    prompt_id: int,
    version: Optional[int] = Query(default=None, description="筛选特定版本的评论"),
    comment_type: Optional[str] = Query(default=None, description="筛选评论类型"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取 Prompt 的评论列表"""
    # 验证 Prompt 存在
    prompt = db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt 不存在")
    
    # 构建查询
    statement = select(PromptComment).where(
        PromptComment.prompt_id == prompt_id,
        PromptComment.parent_id == None  # 只查询顶级评论
    )
    
    if version is not None:
        statement = statement.where(PromptComment.version == version)
    
    if comment_type:
        statement = statement.where(PromptComment.comment_type == comment_type)
    
    statement = statement.order_by(desc(PromptComment.created_at))
    
    comments = db.exec(statement).all()
    
    # 填充用户信息和回复
    result = []
    for comment in comments:
        comment_data = await _enrich_comment(comment, db)
        result.append(comment_data)
    
    return {
        "code": 0,
        "data": result
    }


@router.post("/{prompt_id}/comments")
async def create_comment(
    prompt_id: int,
    data: PromptCommentCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建评论"""
    # 验证 Prompt 存在
    prompt = db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt 不存在")
    
    # 如果是回复，验证父评论存在
    if data.parent_id:
        parent = db.get(PromptComment, data.parent_id)
        if not parent or parent.prompt_id != prompt_id:
            raise HTTPException(status_code=400, detail="父评论不存在")
    
    # 验证提及的用户存在
    if data.mentioned_user_ids:
        for uid in data.mentioned_user_ids:
            user = db.get(User, uid)
            if not user:
                raise HTTPException(status_code=400, detail=f"用户 ID {uid} 不存在")
    
    # 创建评论
    comment = PromptComment(
        prompt_id=prompt_id,
        user_id=current_user.id,
        content=data.content,
        mentioned_user_ids=data.mentioned_user_ids,
        version=data.version,
        parent_id=data.parent_id,
        comment_type=data.comment_type,
        review_status=data.review_status
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # 返回完整信息
    result = await _enrich_comment(comment, db)
    
    return {
        "code": 0,
        "data": result,
        "message": "评论成功"
    }


@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    data: PromptCommentUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新评论"""
    comment = db.get(PromptComment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 只有作者可以编辑内容
    if data.content is not None:
        if comment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="只能编辑自己的评论")
        comment.content = data.content
        comment.is_edited = True
    
    # 更新评审状态（Prompt 作者或管理员可以操作）
    if data.review_status is not None:
        prompt = db.get(Prompt, comment.prompt_id)
        if prompt.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="无权限更新评审状态")
        comment.review_status = data.review_status
    
    comment.updated_at = datetime.utcnow()
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    result = await _enrich_comment(comment, db)
    
    return {
        "code": 0,
        "data": result,
        "message": "更新成功"
    }


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除评论"""
    comment = db.get(PromptComment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 只有作者或管理员可以删除
    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限删除此评论")
    
    # 删除所有回复
    replies = db.exec(
        select(PromptComment).where(PromptComment.parent_id == comment_id)
    ).all()
    for reply in replies:
        db.delete(reply)
    
    db.delete(comment)
    db.commit()
    
    return {
        "code": 0,
        "message": "删除成功"
    }


@router.get("/{prompt_id}/comments/stats")
async def get_comment_stats(
    prompt_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取评论统计"""
    # 总评论数
    total = db.exec(
        select(PromptComment).where(PromptComment.prompt_id == prompt_id)
    ).all()
    
    # 按类型统计
    comments_count = len([c for c in total if c.comment_type == "comment"])
    reviews_count = len([c for c in total if c.comment_type == "review"])
    suggestions_count = len([c for c in total if c.comment_type == "suggestion"])
    
    # 评审状态统计
    pending_reviews = len([c for c in total if c.review_status == "pending"])
    approved_reviews = len([c for c in total if c.review_status == "approved"])
    rejected_reviews = len([c for c in total if c.review_status == "rejected"])
    
    return {
        "code": 0,
        "data": {
            "total": len(total),
            "comments": comments_count,
            "reviews": reviews_count,
            "suggestions": suggestions_count,
            "pending_reviews": pending_reviews,
            "approved_reviews": approved_reviews,
            "rejected_reviews": rejected_reviews
        }
    }


@router.get("/users/search")
async def search_users(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """搜索用户（用于@提及）"""
    statement = select(User).where(
        User.username.contains(keyword)
    ).limit(limit)
    
    users = db.exec(statement).all()
    
    return {
        "code": 0,
        "data": [
            {
                "id": u.id,
                "username": u.username,
                "avatar_url": u.avatar_url
            }
            for u in users
        ]
    }


async def _enrich_comment(comment: PromptComment, db: Session) -> dict:
    """填充评论的额外信息"""
    # 获取用户信息
    user = db.get(User, comment.user_id)
    
    # 获取被提及用户信息
    mentioned_users = []
    if comment.mentioned_user_ids:
        for uid in comment.mentioned_user_ids:
            u = db.get(User, uid)
            if u:
                mentioned_users.append({
                    "id": u.id,
                    "username": u.username,
                    "avatar_url": u.avatar_url
                })
    
    # 获取回复
    replies_statement = select(PromptComment).where(
        PromptComment.parent_id == comment.id
    ).order_by(PromptComment.created_at)
    replies = db.exec(replies_statement).all()
    
    replies_data = []
    for reply in replies:
        reply_user = db.get(User, reply.user_id)
        replies_data.append({
            "id": reply.id,
            "prompt_id": reply.prompt_id,
            "user_id": reply.user_id,
            "content": reply.content,
            "mentioned_user_ids": reply.mentioned_user_ids,
            "version": reply.version,
            "parent_id": reply.parent_id,
            "comment_type": reply.comment_type,
            "review_status": reply.review_status,
            "is_edited": reply.is_edited,
            "created_at": reply.created_at.isoformat() if reply.created_at else None,
            "updated_at": reply.updated_at.isoformat() if reply.updated_at else None,
            "username": reply_user.username if reply_user else None,
            "avatar_url": reply_user.avatar_url if reply_user else None
        })
    
    return {
        "id": comment.id,
        "prompt_id": comment.prompt_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "mentioned_user_ids": comment.mentioned_user_ids,
        "version": comment.version,
        "parent_id": comment.parent_id,
        "comment_type": comment.comment_type,
        "review_status": comment.review_status,
        "is_edited": comment.is_edited,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
        "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
        "username": user.username if user else None,
        "avatar_url": user.avatar_url if user else None,
        "mentioned_users": mentioned_users,
        "replies": replies_data,
        "reply_count": len(replies_data)
    }
