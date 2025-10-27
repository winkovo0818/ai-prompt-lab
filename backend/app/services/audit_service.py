"""审计日志服务"""
from typing import Optional, Dict
from datetime import datetime
from sqlmodel import Session
from fastapi import Request

from ..models.audit_log import AuditLog, AuditLogCreate


class AuditService:
    """审计日志服务"""
    
    # 敏感操作列表
    SENSITIVE_ACTIONS = {
        'user_login', 'user_logout', 'user_register',
        'user_delete', 'user_update_role',
        'api_key_create', 'api_key_update', 'api_key_delete',
        'config_update', 'security_config_update',
        'prompt_delete', 'data_export',
        'sensitive_word_add', 'sensitive_word_delete'
    }
    
    # 高风险操作
    HIGH_RISK_ACTIONS = {
        'user_delete', 'data_export', 'security_config_update',
        'api_key_delete', 'system_config_update'
    }
    
    @staticmethod
    def log(
        db: Session,
        action: str,
        resource: str,
        description: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        status: str = 'success',
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        记录审计日志
        
        Args:
            db: 数据库会话
            action: 操作类型（如 'user_login', 'prompt_create'）
            resource: 资源类型（如 'user', 'prompt', 'config'）
            description: 操作描述
            其他参数: 见参数说明
        
        Returns:
            创建的审计日志对象
        """
        # 判断是否敏感操作
        is_sensitive = action in AuditService.SENSITIVE_ACTIONS
        
        # 判断风险等级
        if action in AuditService.HIGH_RISK_ACTIONS:
            risk_level = 'high'
        elif is_sensitive:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # 创建日志
        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource=resource,
            resource_id=resource_id,
            description=description,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            status=status,
            error_message=error_message,
            risk_level=risk_level,
            is_sensitive=is_sensitive
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def log_from_request(
        db: Session,
        request: Request,
        action: str,
        resource: str,
        description: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[Dict] = None,
        status: str = 'success',
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        从请求对象记录审计日志（自动提取IP、User-Agent等）
        """
        # 获取真实IP地址（考虑代理）
        ip_address = request.client.host if request.client else None
        if 'x-forwarded-for' in request.headers:
            ip_address = request.headers['x-forwarded-for'].split(',')[0].strip()
        elif 'x-real-ip' in request.headers:
            ip_address = request.headers['x-real-ip']
        
        # 获取User-Agent
        user_agent = request.headers.get('user-agent', '')
        
        return AuditService.log(
            db=db,
            action=action,
            resource=resource,
            description=description,
            user_id=user_id,
            username=username,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request.method,
            request_path=str(request.url.path),
            status=status,
            error_message=error_message
        )
    
    @staticmethod
    def log_login(db: Session, user_id: int, username: str, ip_address: str, success: bool = True):
        """记录登录日志"""
        return AuditService.log(
            db=db,
            action='user_login',
            resource='user',
            description=f"用户 {username} 登录{'成功' if success else '失败'}",
            user_id=user_id if success else None,
            username=username,
            ip_address=ip_address,
            status='success' if success else 'failure'
        )
    
    @staticmethod
    def log_logout(db: Session, user_id: int, username: str):
        """记录登出日志"""
        return AuditService.log(
            db=db,
            action='user_logout',
            resource='user',
            description=f"用户 {username} 退出登录",
            user_id=user_id,
            username=username
        )
    
    @staticmethod
    def log_prompt_action(
        db: Session,
        action: str,
        prompt_id: int,
        user_id: int,
        username: str,
        description: str
    ):
        """记录Prompt相关操作"""
        return AuditService.log(
            db=db,
            action=f'prompt_{action}',
            resource='prompt',
            resource_id=prompt_id,
            description=description,
            user_id=user_id,
            username=username
        )
    
    @staticmethod
    def log_api_key_action(
        db: Session,
        action: str,
        user_id: int,
        username: str,
        description: str,
        details: Optional[Dict] = None
    ):
        """记录API密钥操作"""
        return AuditService.log(
            db=db,
            action=f'api_key_{action}',
            resource='api_key',
            description=description,
            user_id=user_id,
            username=username,
            details=details
        )
    
    @staticmethod
    def log_security_event(
        db: Session,
        event_type: str,
        description: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None
    ):
        """记录安全事件"""
        return AuditService.log(
            db=db,
            action=f'security_{event_type}',
            resource='security',
            description=description,
            user_id=user_id,
            username=username,
            details=details,
            ip_address=ip_address,
            status='warning'
        )
    
    @staticmethod
    def clean_old_logs(db: Session, retention_days: int = 90):
        """清理过期日志"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # 删除过期的非敏感日志
        deleted_count = db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date,
            AuditLog.is_sensitive == False
        ).delete()
        
        db.commit()
        
        return deleted_count

