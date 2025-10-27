"""审计日志模型"""
from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON, Text


class AuditLog(SQLModel, table=True):
    """审计日志表"""
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 用户信息
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    username: Optional[str] = Field(default=None, max_length=100)
    
    # 操作信息
    action: str = Field(max_length=100, index=True)  # 操作类型
    resource: str = Field(max_length=100, index=True)  # 资源类型
    resource_id: Optional[int] = None  # 资源ID
    
    # 操作详情
    description: str = Field(sa_column=Column(Text))  # 操作描述
    details: Optional[Dict] = Field(default=None, sa_column=Column(JSON))  # 详细信息
    
    # 请求信息
    ip_address: Optional[str] = Field(default=None, max_length=45)  # 支持IPv6
    user_agent: Optional[str] = Field(default=None, max_length=500)
    request_method: Optional[str] = Field(default=None, max_length=10)
    request_path: Optional[str] = Field(default=None, max_length=500)
    
    # 结果信息
    status: str = Field(max_length=20, index=True)  # success, failure, warning
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # 安全相关
    risk_level: str = Field(default='low', max_length=20)  # low, medium, high, critical
    is_sensitive: bool = Field(default=False)  # 是否敏感操作
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class SecurityConfig(SQLModel, table=True):
    """安全配置表"""
    __tablename__ = "security_configs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    
    # 配置类型：global, user
    config_type: str = Field(max_length=20, default='global')
    
    # IP白名单
    ip_whitelist: Optional[list] = Field(default=None, sa_column=Column(JSON))
    ip_whitelist_enabled: bool = Field(default=False)
    
    # 访问频率限制
    rate_limit_enabled: bool = Field(default=True)
    max_requests_per_minute: int = Field(default=60)
    max_requests_per_hour: int = Field(default=1000)
    
    # 内容审核
    content_audit_enabled: bool = Field(default=True)
    auto_mask_sensitive_info: bool = Field(default=True)
    block_sensitive_words: bool = Field(default=True)
    
    # 敏感词库
    custom_sensitive_words: Optional[list] = Field(default=None, sa_column=Column(JSON))
    
    # API密钥安全
    api_key_encryption_enabled: bool = Field(default=True)
    api_key_rotation_days: Optional[int] = None  # API密钥轮换天数
    
    # 会话安全
    session_timeout_minutes: int = Field(default=480)  # 8小时
    max_concurrent_sessions: int = Field(default=5)
    
    # 审计日志
    audit_log_retention_days: int = Field(default=90)  # 日志保留天数
    log_all_operations: bool = Field(default=True)
    
    # 其他配置
    extra_config: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SensitiveWord(SQLModel, table=True):
    """敏感词表"""
    __tablename__ = "sensitive_words"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    word: str = Field(max_length=100, index=True, unique=True)
    category: str = Field(max_length=50, index=True)  # political, nsfw, illegal, etc.
    severity: int = Field(default=50)  # 严重程度 0-100
    
    is_active: bool = Field(default=True)
    is_system: bool = Field(default=False)  # 是否系统内置
    
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============ 请求/响应模型 ============

class AuditLogCreate(SQLModel):
    """创建审计日志"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    resource: str
    resource_id: Optional[int] = None
    description: str
    details: Optional[Dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    status: str = 'success'
    error_message: Optional[str] = None
    risk_level: str = 'low'
    is_sensitive: bool = False


class AuditLogResponse(SQLModel):
    """审计日志响应"""
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    resource: str
    resource_id: Optional[int]
    description: str
    details: Optional[Dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_method: Optional[str]
    request_path: Optional[str]
    status: str
    error_message: Optional[str]
    risk_level: str
    is_sensitive: bool
    created_at: datetime


class SecurityConfigUpdate(SQLModel):
    """安全配置更新"""
    ip_whitelist: Optional[list] = None
    ip_whitelist_enabled: Optional[bool] = None
    rate_limit_enabled: Optional[bool] = None
    max_requests_per_minute: Optional[int] = None
    max_requests_per_hour: Optional[int] = None
    content_audit_enabled: Optional[bool] = None
    auto_mask_sensitive_info: Optional[bool] = None
    block_sensitive_words: Optional[bool] = None
    custom_sensitive_words: Optional[list] = None
    api_key_encryption_enabled: Optional[bool] = None
    session_timeout_minutes: Optional[int] = None
    audit_log_retention_days: Optional[int] = None


class SecurityConfigResponse(SQLModel):
    """安全配置响应"""
    id: int
    config_type: str
    ip_whitelist: Optional[list]
    ip_whitelist_enabled: bool
    rate_limit_enabled: bool
    max_requests_per_minute: int
    max_requests_per_hour: int
    content_audit_enabled: bool
    auto_mask_sensitive_info: bool
    block_sensitive_words: bool
    api_key_encryption_enabled: bool
    session_timeout_minutes: int
    audit_log_retention_days: int
    created_at: datetime
    updated_at: datetime


class SensitiveWordCreate(SQLModel):
    """创建敏感词"""
    word: str
    category: str
    severity: int = 50


class SensitiveWordResponse(SQLModel):
    """敏感词响应"""
    id: int
    word: str
    category: str
    severity: int
    is_active: bool
    is_system: bool
    created_at: datetime

