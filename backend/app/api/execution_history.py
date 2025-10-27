from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, and_
from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.execution_history import ExecutionHistory, ExecutionHistoryResponse
from ..utils.response import success_response, error_response

router = APIRouter(prefix="/api/execution_history", tags=["执行历史"])


@router.get("/search", response_model=dict)
async def search_execution_history(
    prompt_id: Optional[int] = None,
    prompt_content: Optional[str] = None,
    prompt_version: Optional[int] = None,
    variables: Optional[str] = None,  # JSON字符串
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """
    搜索执行历史记录
    根据 prompt_id、version、variables、model 等参数查找是否有匹配的历史记录
    """
    
    # 构建查询条件
    conditions = [ExecutionHistory.user_id == current_user.id]
    
    if prompt_id is not None:
        conditions.append(ExecutionHistory.prompt_id == prompt_id)
    
    if prompt_content is not None:
        conditions.append(ExecutionHistory.prompt_content == prompt_content)
    
    if prompt_version is not None:
        conditions.append(ExecutionHistory.prompt_version == prompt_version)
    
    if model is not None:
        conditions.append(ExecutionHistory.model == model)
    
    if temperature is not None:
        conditions.append(ExecutionHistory.temperature == temperature)
    
    if max_tokens is not None:
        conditions.append(ExecutionHistory.max_tokens == max_tokens)
    
    # 查询
    statement = select(ExecutionHistory).where(and_(*conditions)).order_by(
        ExecutionHistory.created_at.desc()
    ).limit(1)  # 只取最新的一条
    
    result = db.exec(statement).first()
    
    if result:
        # 如果提供了 variables，需要精确匹配
        if variables is not None:
            import json
            try:
                search_vars = json.loads(variables)
                if result.variables != search_vars:
                    return success_response(data=None, message="未找到匹配的历史记录")
            except:
                pass
        
        response = ExecutionHistoryResponse(
            id=result.id,
            user_id=result.user_id,
            prompt_id=result.prompt_id,
            prompt_content=result.prompt_content,
            prompt_version=result.prompt_version,
            variables=result.variables,
            final_prompt=result.final_prompt,
            model=result.model,
            temperature=result.temperature,
            max_tokens=result.max_tokens,
            output=result.output,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            total_tokens=result.total_tokens,
            cost=result.cost,
            response_time=result.response_time,
            created_at=result.created_at,
            is_cached=True
        )
        
        return success_response(data=response.model_dump(), message="找到历史记录")
    else:
        return success_response(data=None, message="未找到匹配的历史记录")


@router.get("/list", response_model=dict)
async def get_execution_history_list(
    prompt_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取执行历史列表"""
    
    conditions = [ExecutionHistory.user_id == current_user.id]
    
    if prompt_id is not None:
        conditions.append(ExecutionHistory.prompt_id == prompt_id)
    
    statement = select(ExecutionHistory).where(and_(*conditions)).order_by(
        ExecutionHistory.created_at.desc()
    )
    
    # 统计总数
    total = len(db.exec(statement).all())
    
    # 分页查询
    statement = statement.offset(skip).limit(limit)
    results = db.exec(statement).all()
    
    items = []
    for result in results:
        response = ExecutionHistoryResponse(
            id=result.id,
            user_id=result.user_id,
            prompt_id=result.prompt_id,
            prompt_content=result.prompt_content,
            prompt_version=result.prompt_version,
            variables=result.variables,
            final_prompt=result.final_prompt,
            model=result.model,
            temperature=result.temperature,
            max_tokens=result.max_tokens,
            output=result.output,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            total_tokens=result.total_tokens,
            cost=result.cost,
            response_time=result.response_time,
            created_at=result.created_at,
            is_cached=True
        )
        items.append(response.model_dump())
    
    return success_response(data={
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    })


@router.delete("/{history_id}", response_model=dict)
async def delete_execution_history(
    history_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """删除执行历史记录"""
    
    history = db.get(ExecutionHistory, history_id)
    
    if not history:
        return error_response(code=4001, message="历史记录不存在")
    
    # 权限检查
    if history.user_id != current_user.id:
        return error_response(code=4002, message="无权删除该历史记录")
    
    db.delete(history)
    db.commit()
    
    return success_response(message="历史记录删除成功")

