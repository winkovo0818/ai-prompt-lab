"""安全管理 API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlmodel import Session, select, func
from datetime import datetime, timedelta

from ..core.database import get_session
from ..core.deps import get_current_active_user, require_admin
from ..models.user import User
from ..models.audit_log import (
    AuditLog, AuditLogResponse,
    SecurityConfig, SecurityConfigUpdate, SecurityConfigResponse,
    SensitiveWord, SensitiveWordCreate, SensitiveWordResponse
)
from ..services.security_service import SecurityService
from ..services.audit_service import AuditService
from ..utils.response import success_response, error_response

router = APIRouter(prefix="/api/security", tags=["安全管理"])


# ============================================
# 内容审核 API
# ============================================

@router.post("/audit/content", response_model=dict)
async def audit_content(
    data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """内容安全审核"""
    content = data.get('content', '')
    auto_mask = data.get('auto_mask', False)
    
    if not content:
        return error_response(code=4001, message="内容不能为空")
    
    try:
        result = SecurityService.content_audit(content, auto_mask)
        
        # 记录审计日志
        if not result['is_approved']:
            AuditService.log(
                db=db,
                action='content_audit_blocked',
                resource='content',
                description=f"内容审核未通过（风险等级：{result['sensitive_words']['risk_level']}）",
                user_id=current_user.id,
                username=current_user.username,
                details={'violations': result['sensitive_words']['violations']},
                status='warning'
            )
        
        return success_response(data=result)
    except Exception as e:
        return error_response(code=5001, message=f"审核失败: {str(e)}")


@router.post("/mask/sensitive-info", response_model=dict)
async def mask_sensitive_info(
    data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """脱敏敏感信息"""
    content = data.get('content', '')
    mask_char = data.get('mask_char', '*')
    
    if not content:
        return error_response(code=4001, message="内容不能为空")
    
    try:
        masked_content, masked_items = SecurityService.mask_sensitive_info(content, mask_char)
        
        return success_response(data={
            'original_length': len(content),
            'masked_content': masked_content,
            'masked_items': masked_items,
            'count': len(masked_items)
        })
    except Exception as e:
        return error_response(code=5001, message=f"脱敏失败: {str(e)}")


@router.post("/detect/sensitive-info", response_model=dict)
async def detect_sensitive_info(
    data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """检测敏感信息"""
    content = data.get('content', '')
    
    if not content:
        return error_response(code=4001, message="内容不能为空")
    
    try:
        result = SecurityService.detect_sensitive_info(content)
        return success_response(data=result)
    except Exception as e:
        return error_response(code=5001, message=f"检测失败: {str(e)}")


# ============================================
# 审计日志 API
# ============================================

@router.get("/audit-logs", response_model=dict)
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = None,
    resource: Optional[str] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """获取审计日志列表（管理员）"""
    
    statement = select(AuditLog)
    
    # 筛选条件
    if action:
        statement = statement.where(AuditLog.action == action)
    if resource:
        statement = statement.where(AuditLog.resource == resource)
    if status:
        statement = statement.where(AuditLog.status == status)
    if risk_level:
        statement = statement.where(AuditLog.risk_level == risk_level)
    
    # 日期范围
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            statement = statement.where(AuditLog.created_at >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            statement = statement.where(AuditLog.created_at <= end_dt)
        except ValueError:
            pass
    
    # 排序
    statement = statement.order_by(AuditLog.created_at.desc())
    
    # 总数
    count_statement = select(func.count()).select_from(statement.subquery())
    total = db.exec(count_statement).one()
    
    # 分页
    statement = statement.offset(skip).limit(limit)
    logs = db.exec(statement).all()
    
    # 转换为响应格式
    items = [AuditLogResponse.model_validate(log) for log in logs]
    
    return success_response(data={
        "items": [item.model_dump() for item in items],
        "total": total,
        "skip": skip,
        "limit": limit
    })


@router.get("/audit-logs/my", response_model=dict)
async def get_my_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取我的审计日志"""
    
    statement = select(AuditLog).where(AuditLog.user_id == current_user.id)
    
    if action:
        statement = statement.where(AuditLog.action == action)
    
    statement = statement.order_by(AuditLog.created_at.desc())
    
    # 总数
    count_statement = select(func.count()).select_from(statement.subquery())
    total = db.exec(count_statement).one()
    
    # 分页
    statement = statement.offset(skip).limit(limit)
    logs = db.exec(statement).all()
    
    items = [AuditLogResponse.model_validate(log) for log in logs]
    
    return success_response(data={
        "items": [item.model_dump() for item in items],
        "total": total,
        "skip": skip,
        "limit": limit
    })


@router.get("/audit-logs/stats", response_model=dict)
async def get_audit_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """获取审计日志统计（管理员）"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # 总操作数
    total_operations = db.exec(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= cutoff_date)
    ).one()
    
    # 失败操作数
    failed_operations = db.exec(
        select(func.count(AuditLog.id)).where(
            AuditLog.created_at >= cutoff_date,
            AuditLog.status == 'failure'
        )
    ).one()
    
    # 高风险操作数
    high_risk_operations = db.exec(
        select(func.count(AuditLog.id)).where(
            AuditLog.created_at >= cutoff_date,
            AuditLog.risk_level == 'high'
        )
    ).one()
    
    # 敏感操作数
    sensitive_operations = db.exec(
        select(func.count(AuditLog.id)).where(
            AuditLog.created_at >= cutoff_date,
            AuditLog.is_sensitive == True
        )
    ).one()
    
    # 按操作类型统计
    action_stats = db.exec(
        select(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).where(
            AuditLog.created_at >= cutoff_date
        ).group_by(AuditLog.action).order_by(func.count(AuditLog.id).desc()).limit(10)
    ).all()
    
    return success_response(data={
        "total_operations": total_operations,
        "failed_operations": failed_operations,
        "high_risk_operations": high_risk_operations,
        "sensitive_operations": sensitive_operations,
        "top_actions": [{"action": action, "count": count} for action, count in action_stats],
        "period_days": days
    })


# ============================================
# 安全配置 API
# ============================================

@router.get("/config", response_model=dict)
async def get_security_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """获取安全配置（管理员）"""
    
    # 获取全局配置
    statement = select(SecurityConfig).where(SecurityConfig.config_type == 'global')
    config = db.exec(statement).first()
    
    if not config:
        # 创建默认配置
        config = SecurityConfig(config_type='global')
        db.add(config)
        db.commit()
        db.refresh(config)
    
    response = SecurityConfigResponse.model_validate(config)
    return success_response(data=response.model_dump())


@router.put("/config", response_model=dict)
async def update_security_config(
    data: SecurityConfigUpdate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """更新安全配置（管理员）"""
    
    # 获取配置
    statement = select(SecurityConfig).where(SecurityConfig.config_type == 'global')
    config = db.exec(statement).first()
    
    if not config:
        config = SecurityConfig(config_type='global')
        db.add(config)
    
    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(config)
    
    # 记录审计日志
    AuditService.log_from_request(
        db=db,
        request=request,
        action='security_config_update',
        resource='security_config',
        description="更新安全配置",
        user_id=current_user.id,
        username=current_user.username,
        details=update_data
    )
    
    response = SecurityConfigResponse.model_validate(config)
    return success_response(data=response.model_dump(), message="安全配置已更新")


# ============================================
# 敏感词管理 API
# ============================================

@router.get("/sensitive-words", response_model=dict)
async def get_sensitive_words(
    category: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """获取敏感词列表（管理员）"""
    
    statement = select(SensitiveWord).where(SensitiveWord.is_active == True)
    
    if category:
        statement = statement.where(SensitiveWord.category == category)
    
    statement = statement.order_by(SensitiveWord.severity.desc(), SensitiveWord.word)
    
    words = db.exec(statement).all()
    
    items = [SensitiveWordResponse.model_validate(word) for word in words]
    
    return success_response(data={
        "items": [item.model_dump() for item in items],
        "total": len(items)
    })


@router.post("/sensitive-words", response_model=dict)
async def add_sensitive_word(
    data: SensitiveWordCreate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """添加敏感词（管理员）"""
    
    # 检查是否已存在
    existing = db.exec(
        select(SensitiveWord).where(SensitiveWord.word == data.word)
    ).first()
    
    if existing:
        return error_response(code=4002, message="该敏感词已存在")
    
    # 创建敏感词
    word = SensitiveWord(
        word=data.word,
        category=data.category,
        severity=data.severity,
        is_system=False,
        created_by=current_user.id
    )
    
    db.add(word)
    db.commit()
    db.refresh(word)
    
    # 同时添加到运行时敏感词库
    SecurityService.add_custom_sensitive_word(data.word, data.category)
    
    # 记录审计日志
    AuditService.log_from_request(
        db=db,
        request=request,
        action='sensitive_word_add',
        resource='sensitive_word',
        resource_id=word.id,
        description=f"添加敏感词: {data.word}",
        user_id=current_user.id,
        username=current_user.username
    )
    
    response = SensitiveWordResponse.model_validate(word)
    return success_response(data=response.model_dump(), message="敏感词已添加")


@router.delete("/sensitive-words/{word_id}", response_model=dict)
async def delete_sensitive_word(
    word_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """删除敏感词（管理员）"""
    
    word = db.get(SensitiveWord, word_id)
    
    if not word:
        return error_response(code=4003, message="敏感词不存在")
    
    if word.is_system:
        return error_response(code=4004, message="不能删除系统内置敏感词")
    
    # 删除
    word_text = word.word
    word_category = word.category
    
    db.delete(word)
    db.commit()
    
    # 从运行时敏感词库移除
    SecurityService.remove_custom_sensitive_word(word_text, word_category)
    
    # 记录审计日志
    AuditService.log_from_request(
        db=db,
        request=request,
        action='sensitive_word_delete',
        resource='sensitive_word',
        resource_id=word_id,
        description=f"删除敏感词: {word_text}",
        user_id=current_user.id,
        username=current_user.username
    )
    
    return success_response(message="敏感词已删除")


@router.get("/sensitive-words/categories", response_model=dict)
async def get_sensitive_word_categories(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """获取敏感词分类列表"""
    
    categories = db.exec(
        select(SensitiveWord.category, func.count(SensitiveWord.id).label('count'))
        .where(SensitiveWord.is_active == True)
        .group_by(SensitiveWord.category)
    ).all()
    
    return success_response(data={
        "categories": [
            {"name": category, "count": count}
            for category, count in categories
        ]
    })

