"""
使用统计 API
提供 API 调用量、Token 消耗、成本估算等统计数据
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func, desc
from sqlalchemy import cast, Date

from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.execution_history import ExecutionHistory
from ..models.prompt import Prompt

router = APIRouter(prefix="/api/statistics", tags=["使用统计"])


@router.get("/overview")
async def get_overview(
    days: int = Query(default=30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取统计概览
    
    返回总调用次数、总 Token 消耗、总成本、平均响应时间
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 查询该用户在时间范围内的统计
    statement = select(
        func.count(ExecutionHistory.id).label("total_calls"),
        func.sum(ExecutionHistory.total_tokens).label("total_tokens"),
        func.sum(ExecutionHistory.input_tokens).label("total_input_tokens"),
        func.sum(ExecutionHistory.output_tokens).label("total_output_tokens"),
        func.sum(ExecutionHistory.cost).label("total_cost"),
        func.avg(ExecutionHistory.response_time).label("avg_response_time")
    ).where(
        ExecutionHistory.user_id == current_user.id,
        ExecutionHistory.created_at >= start_date
    )
    
    result = db.exec(statement).first()
    
    return {
        "code": 0,
        "data": {
            "total_calls": result.total_calls or 0,
            "total_tokens": result.total_tokens or 0,
            "total_input_tokens": result.total_input_tokens or 0,
            "total_output_tokens": result.total_output_tokens or 0,
            "total_cost": round(result.total_cost or 0, 4),
            "avg_response_time": round(result.avg_response_time or 0, 3),
            "days": days
        }
    }


@router.get("/daily")
async def get_daily_stats(
    days: int = Query(default=30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取每日统计数据
    
    返回每日 API 调用量、Token 消耗、成本
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 按日期分组统计
    statement = select(
        cast(ExecutionHistory.created_at, Date).label("date"),
        func.count(ExecutionHistory.id).label("calls"),
        func.sum(ExecutionHistory.total_tokens).label("tokens"),
        func.sum(ExecutionHistory.cost).label("cost"),
        func.avg(ExecutionHistory.response_time).label("avg_response_time")
    ).where(
        ExecutionHistory.user_id == current_user.id,
        ExecutionHistory.created_at >= start_date
    ).group_by(
        cast(ExecutionHistory.created_at, Date)
    ).order_by(
        cast(ExecutionHistory.created_at, Date)
    )
    
    results = db.exec(statement).all()
    
    # 填充缺失的日期
    daily_data = []
    date_map = {str(r.date): r for r in results}
    
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days-1-i)).date()
        date_str = str(date)
        
        if date_str in date_map:
            r = date_map[date_str]
            daily_data.append({
                "date": date_str,
                "calls": r.calls,
                "tokens": r.tokens or 0,
                "cost": round(r.cost or 0, 4),
                "avg_response_time": round(r.avg_response_time or 0, 3)
            })
        else:
            daily_data.append({
                "date": date_str,
                "calls": 0,
                "tokens": 0,
                "cost": 0,
                "avg_response_time": 0
            })
    
    return {
        "code": 0,
        "data": daily_data
    }


@router.get("/top-prompts")
async def get_top_prompts(
    limit: int = Query(default=10, ge=1, le=50, description="返回数量"),
    days: int = Query(default=30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取最常用的 Prompt
    
    返回使用次数最多的 Prompt 列表
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 按 prompt_id 分组统计
    statement = select(
        ExecutionHistory.prompt_id,
        func.count(ExecutionHistory.id).label("use_count"),
        func.sum(ExecutionHistory.total_tokens).label("total_tokens"),
        func.sum(ExecutionHistory.cost).label("total_cost"),
        func.avg(ExecutionHistory.response_time).label("avg_response_time")
    ).where(
        ExecutionHistory.user_id == current_user.id,
        ExecutionHistory.created_at >= start_date,
        ExecutionHistory.prompt_id.isnot(None)
    ).group_by(
        ExecutionHistory.prompt_id
    ).order_by(
        desc("use_count")
    ).limit(limit)
    
    results = db.exec(statement).all()
    
    # 获取 Prompt 详情
    top_prompts = []
    for r in results:
        prompt = db.get(Prompt, r.prompt_id)
        if prompt:
            top_prompts.append({
                "prompt_id": r.prompt_id,
                "title": prompt.title,
                "use_count": r.use_count,
                "total_tokens": r.total_tokens or 0,
                "total_cost": round(r.total_cost or 0, 4),
                "avg_response_time": round(r.avg_response_time or 0, 3)
            })
    
    return {
        "code": 0,
        "data": top_prompts
    }


@router.get("/model-usage")
async def get_model_usage(
    days: int = Query(default=30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取模型使用统计
    
    返回各模型的使用次数和消耗
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 按模型分组统计
    statement = select(
        ExecutionHistory.model,
        func.count(ExecutionHistory.id).label("calls"),
        func.sum(ExecutionHistory.total_tokens).label("tokens"),
        func.sum(ExecutionHistory.cost).label("cost"),
        func.avg(ExecutionHistory.response_time).label("avg_response_time")
    ).where(
        ExecutionHistory.user_id == current_user.id,
        ExecutionHistory.created_at >= start_date
    ).group_by(
        ExecutionHistory.model
    ).order_by(
        desc("calls")
    )
    
    results = db.exec(statement).all()
    
    model_usage = []
    for r in results:
        model_usage.append({
            "model": r.model,
            "calls": r.calls,
            "tokens": r.tokens or 0,
            "cost": round(r.cost or 0, 4),
            "avg_response_time": round(r.avg_response_time or 0, 3)
        })
    
    return {
        "code": 0,
        "data": model_usage
    }


@router.get("/hourly")
async def get_hourly_stats(
    days: int = Query(default=7, ge=1, le=30, description="统计天数"),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取每小时统计数据（用于热力图）
    
    返回每个小时的 API 调用分布
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 按小时分组统计
    statement = select(
        func.extract('hour', ExecutionHistory.created_at).label("hour"),
        func.count(ExecutionHistory.id).label("calls")
    ).where(
        ExecutionHistory.user_id == current_user.id,
        ExecutionHistory.created_at >= start_date
    ).group_by(
        func.extract('hour', ExecutionHistory.created_at)
    ).order_by("hour")
    
    results = db.exec(statement).all()
    
    # 填充 24 小时
    hourly_data = [0] * 24
    for r in results:
        hour = int(r.hour)
        hourly_data[hour] = r.calls
    
    return {
        "code": 0,
        "data": {
            "hours": list(range(24)),
            "calls": hourly_data
        }
    }
