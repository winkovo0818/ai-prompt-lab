"""API 配额管理"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..core.database import get_session
from ..core.deps import get_current_active_user, get_current_admin_user
from ..models.user import User
from ..models.api_quota import ApiQuota, ApiUsage, QuotaUpdateRequest, QuotaType
from ..services.quota_service import QuotaService
from ..utils.response import success_response, error_response

router = APIRouter(prefix="/api/quota", tags=["配额管理"])


@router.get("/status")
async def get_my_quota_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取当前用户的配额状态"""
    status = QuotaService.get_quota_status(db, current_user.id)
    return success_response(data=status)


@router.get("/usage/history")
async def get_usage_history(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取使用历史"""
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    statement = select(ApiUsage).where(
        ApiUsage.user_id == current_user.id,
        ApiUsage.usage_date >= start_date
    ).order_by(ApiUsage.usage_date.desc())
    
    usages = db.exec(statement).all()
    
    return success_response(data=[{
        'date': u.usage_date.strftime('%Y-%m-%d'),
        'requests': u.request_count,
        'tokens': u.total_tokens,
        'cost': round(u.total_cost, 4),
        'model_usage': u.model_usage
    } for u in usages])


# ============ 管理员接口 ============

@router.get("/admin/list")
async def list_all_quotas(
    quota_type: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """[管理员] 列出所有配额配置"""
    statement = select(ApiQuota)
    
    if quota_type:
        statement = statement.where(ApiQuota.quota_type == quota_type)
    
    statement = statement.offset(skip).limit(limit)
    quotas = db.exec(statement).all()
    
    # 获取用户信息
    result = []
    for q in quotas:
        item = {
            'id': q.id,
            'quota_type': q.quota_type,
            'target_id': q.target_id,
            'requests_per_minute': q.requests_per_minute,
            'requests_per_hour': q.requests_per_hour,
            'requests_per_day': q.requests_per_day,
            'requests_per_month': q.requests_per_month,
            'tokens_per_day': q.tokens_per_day,
            'tokens_per_month': q.tokens_per_month,
            'cost_per_day': q.cost_per_day,
            'cost_per_month': q.cost_per_month,
            'is_active': q.is_active,
            'description': q.description,
            'created_at': q.created_at,
            'updated_at': q.updated_at,
        }
        
        # 获取目标名称
        if q.quota_type == QuotaType.USER:
            user = db.get(User, q.target_id)
            item['target_name'] = user.username if user else f"用户 #{q.target_id}"
        else:
            item['target_name'] = f"团队 #{q.target_id}"
        
        result.append(item)
    
    return success_response(data=result)


@router.post("/admin/user/{user_id}")
async def set_user_quota(
    user_id: int,
    quota_data: QuotaUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """[管理员] 设置用户配额"""
    # 检查用户是否存在
    user = db.get(User, user_id)
    if not user:
        return error_response(code=4004, message="用户不存在")
    
    quota = QuotaService.set_user_quota(
        db, user_id,
        requests_per_minute=quota_data.requests_per_minute,
        requests_per_hour=quota_data.requests_per_hour,
        requests_per_day=quota_data.requests_per_day,
        requests_per_month=quota_data.requests_per_month,
        tokens_per_day=quota_data.tokens_per_day,
        tokens_per_month=quota_data.tokens_per_month,
        cost_per_day=quota_data.cost_per_day,
        cost_per_month=quota_data.cost_per_month,
        is_active=quota_data.is_active,
        description=quota_data.description
    )
    
    return success_response(
        data={
            'id': quota.id,
            'quota_type': quota.quota_type,
            'target_id': quota.target_id,
            'target_name': user.username
        },
        message=f"用户 {user.username} 的配额已更新"
    )


@router.post("/admin/team/{team_id}")
async def set_team_quota(
    team_id: int,
    quota_data: QuotaUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """[管理员] 设置团队配额"""
    quota = QuotaService.set_team_quota(
        db, team_id,
        requests_per_minute=quota_data.requests_per_minute,
        requests_per_hour=quota_data.requests_per_hour,
        requests_per_day=quota_data.requests_per_day,
        requests_per_month=quota_data.requests_per_month,
        tokens_per_day=quota_data.tokens_per_day,
        tokens_per_month=quota_data.tokens_per_month,
        cost_per_day=quota_data.cost_per_day,
        cost_per_month=quota_data.cost_per_month,
        is_active=quota_data.is_active,
        description=quota_data.description
    )
    
    return success_response(
        data={
            'id': quota.id,
            'quota_type': quota.quota_type,
            'target_id': quota.target_id
        },
        message=f"团队 #{team_id} 的配额已更新"
    )


@router.delete("/admin/{quota_id}")
async def delete_quota(
    quota_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """[管理员] 删除配额配置"""
    quota = db.get(ApiQuota, quota_id)
    if not quota:
        return error_response(code=4004, message="配额配置不存在")
    
    db.delete(quota)
    db.commit()
    
    return success_response(message="配额配置已删除")


@router.get("/admin/user/{user_id}/status")
async def get_user_quota_status(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """[管理员] 获取指定用户的配额状态"""
    user = db.get(User, user_id)
    if not user:
        return error_response(code=4004, message="用户不存在")
    
    status = QuotaService.get_quota_status(db, user_id)
    status['username'] = user.username
    
    return success_response(data=status)


@router.get("/admin/usage/all")
async def get_all_usage(
    days: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """[管理员] 获取所有用户的使用汇总"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 按用户汇总
    statement = select(
        ApiUsage.user_id,
        func.sum(ApiUsage.request_count).label('total_requests'),
        func.sum(ApiUsage.total_tokens).label('total_tokens'),
        func.sum(ApiUsage.total_cost).label('total_cost')
    ).where(
        ApiUsage.usage_date >= start_date
    ).group_by(ApiUsage.user_id)
    
    results = db.exec(statement).all()
    
    # 获取用户信息
    usage_list = []
    for r in results:
        user = db.get(User, r.user_id)
        usage_list.append({
            'user_id': r.user_id,
            'username': user.username if user else f"用户 #{r.user_id}",
            'total_requests': r.total_requests or 0,
            'total_tokens': r.total_tokens or 0,
            'total_cost': round(r.total_cost or 0, 4)
        })
    
    # 按请求数排序
    usage_list.sort(key=lambda x: x['total_requests'], reverse=True)
    
    return success_response(data={
        'period_days': days,
        'users': usage_list
    })
