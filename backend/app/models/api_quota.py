"""API 配额模型"""
from typing import Optional
from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Text


class QuotaType(str, Enum):
    """配额类型"""
    USER = "user"
    TEAM = "team"


class QuotaPeriod(str, Enum):
    """配额周期"""
    DAILY = "daily"
    MONTHLY = "monthly"
    UNLIMITED = "unlimited"


class ApiQuota(SQLModel, table=True):
    """API 配额配置表"""
    __tablename__ = "api_quotas"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 关联目标
    quota_type: str = Field(max_length=20, index=True)  # user / team
    target_id: int = Field(index=True)  # user_id 或 team_id
    
    # 配额限制
    requests_per_minute: int = Field(default=60)  # 每分钟请求数
    requests_per_hour: int = Field(default=1000)  # 每小时请求数
    requests_per_day: int = Field(default=10000)  # 每天请求数
    requests_per_month: int = Field(default=100000)  # 每月请求数
    
    # Token 限制
    tokens_per_day: int = Field(default=1000000)  # 每天 token 数
    tokens_per_month: int = Field(default=10000000)  # 每月 token 数
    
    # 费用限制
    cost_per_day: float = Field(default=10.0)  # 每天费用限制 (USD)
    cost_per_month: float = Field(default=100.0)  # 每月费用限制 (USD)
    
    # 状态
    is_active: bool = Field(default=True)
    description: Optional[str] = Field(default=None, max_length=500)
    
    # 时间
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApiUsage(SQLModel, table=True):
    """API 使用记录表（按日期汇总）"""
    __tablename__ = "api_usage"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 关联
    user_id: int = Field(index=True)
    team_id: Optional[int] = Field(default=None, index=True)
    
    # 时间维度
    usage_date: datetime = Field(index=True)  # 日期（精确到天）
    
    # 使用量统计
    request_count: int = Field(default=0)  # 请求次数
    total_tokens: int = Field(default=0)  # 总 token 数
    input_tokens: int = Field(default=0)  # 输入 token 数
    output_tokens: int = Field(default=0)  # 输出 token 数
    total_cost: float = Field(default=0.0)  # 总费用
    
    # 详细记录
    model_usage: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON: {model: {count, tokens, cost}}
    
    # 时间
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============ Response Models ============

class ApiQuotaResponse(SQLModel):
    """配额响应模型"""
    id: int
    quota_type: str
    target_id: int
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    requests_per_month: int
    tokens_per_day: int
    tokens_per_month: int
    cost_per_day: float
    cost_per_month: float
    is_active: bool
    description: Optional[str]


class ApiUsageResponse(SQLModel):
    """使用量响应模型"""
    user_id: int
    team_id: Optional[int]
    usage_date: datetime
    request_count: int
    total_tokens: int
    total_cost: float


class QuotaStatusResponse(SQLModel):
    """配额状态响应"""
    # 当前配额
    quota: Optional[ApiQuotaResponse]
    
    # 今日使用量
    today_requests: int = 0
    today_tokens: int = 0
    today_cost: float = 0.0
    
    # 本月使用量
    month_requests: int = 0
    month_tokens: int = 0
    month_cost: float = 0.0
    
    # 剩余配额
    remaining_requests_today: int = 0
    remaining_tokens_today: int = 0
    remaining_cost_today: float = 0.0
    remaining_requests_month: int = 0
    remaining_tokens_month: int = 0
    remaining_cost_month: float = 0.0
    
    # 使用百分比
    usage_percent_requests: float = 0.0
    usage_percent_tokens: float = 0.0
    usage_percent_cost: float = 0.0


class QuotaUpdateRequest(SQLModel):
    """配额更新请求"""
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    requests_per_month: Optional[int] = None
    tokens_per_day: Optional[int] = None
    tokens_per_month: Optional[int] = None
    cost_per_day: Optional[float] = None
    cost_per_month: Optional[float] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
