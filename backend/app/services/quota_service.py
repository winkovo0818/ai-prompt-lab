"""API 配额服务"""
import json
from typing import Optional, Dict, Tuple
from datetime import datetime, date
from sqlmodel import Session, select, and_

from ..models.api_quota import ApiQuota, ApiUsage, QuotaType
from ..models.user import User


class QuotaService:
    """配额管理服务"""
    
    # 默认配额（用于没有配置的用户）
    DEFAULT_QUOTA = {
        'requests_per_minute': 60,
        'requests_per_hour': 1000,
        'requests_per_day': 10000,
        'requests_per_month': 100000,
        'tokens_per_day': 1000000,
        'tokens_per_month': 10000000,
        'cost_per_day': 10.0,
        'cost_per_month': 100.0,
    }
    
    @classmethod
    def get_user_quota(cls, db: Session, user_id: int) -> Optional[ApiQuota]:
        """获取用户配额配置"""
        statement = select(ApiQuota).where(
            and_(
                ApiQuota.quota_type == QuotaType.USER,
                ApiQuota.target_id == user_id,
                ApiQuota.is_active == True
            )
        )
        return db.exec(statement).first()
    
    @classmethod
    def get_team_quota(cls, db: Session, team_id: int) -> Optional[ApiQuota]:
        """获取团队配额配置"""
        statement = select(ApiQuota).where(
            and_(
                ApiQuota.quota_type == QuotaType.TEAM,
                ApiQuota.target_id == team_id,
                ApiQuota.is_active == True
            )
        )
        return db.exec(statement).first()
    
    @classmethod
    def get_effective_quota(cls, db: Session, user_id: int, team_id: Optional[int] = None) -> Dict:
        """
        获取用户的有效配额（优先级：用户配额 > 团队配额 > 默认配额）
        """
        # 先查用户配额
        user_quota = cls.get_user_quota(db, user_id)
        if user_quota:
            return {
                'requests_per_minute': user_quota.requests_per_minute,
                'requests_per_hour': user_quota.requests_per_hour,
                'requests_per_day': user_quota.requests_per_day,
                'requests_per_month': user_quota.requests_per_month,
                'tokens_per_day': user_quota.tokens_per_day,
                'tokens_per_month': user_quota.tokens_per_month,
                'cost_per_day': user_quota.cost_per_day,
                'cost_per_month': user_quota.cost_per_month,
                'source': 'user',
                'quota_id': user_quota.id
            }
        
        # 再查团队配额
        if team_id:
            team_quota = cls.get_team_quota(db, team_id)
            if team_quota:
                return {
                    'requests_per_minute': team_quota.requests_per_minute,
                    'requests_per_hour': team_quota.requests_per_hour,
                    'requests_per_day': team_quota.requests_per_day,
                    'requests_per_month': team_quota.requests_per_month,
                    'tokens_per_day': team_quota.tokens_per_day,
                    'tokens_per_month': team_quota.tokens_per_month,
                    'cost_per_day': team_quota.cost_per_day,
                    'cost_per_month': team_quota.cost_per_month,
                    'source': 'team',
                    'quota_id': team_quota.id
                }
        
        # 返回默认配额
        return {**cls.DEFAULT_QUOTA, 'source': 'default', 'quota_id': None}
    
    @classmethod
    def get_today_usage(cls, db: Session, user_id: int) -> ApiUsage:
        """获取今日使用量（如果不存在则创建）"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        statement = select(ApiUsage).where(
            and_(
                ApiUsage.user_id == user_id,
                ApiUsage.usage_date == today
            )
        )
        usage = db.exec(statement).first()
        
        if not usage:
            usage = ApiUsage(
                user_id=user_id,
                usage_date=today,
                request_count=0,
                total_tokens=0,
                input_tokens=0,
                output_tokens=0,
                total_cost=0.0
            )
            db.add(usage)
            db.commit()
            db.refresh(usage)
        
        return usage
    
    @classmethod
    def get_month_usage(cls, db: Session, user_id: int) -> Dict:
        """获取本月使用量汇总"""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        statement = select(ApiUsage).where(
            and_(
                ApiUsage.user_id == user_id,
                ApiUsage.usage_date >= month_start
            )
        )
        usages = db.exec(statement).all()
        
        total_requests = sum(u.request_count for u in usages)
        total_tokens = sum(u.total_tokens for u in usages)
        total_cost = sum(u.total_cost for u in usages)
        
        return {
            'request_count': total_requests,
            'total_tokens': total_tokens,
            'total_cost': total_cost
        }
    
    @classmethod
    def check_quota(
        cls, 
        db: Session, 
        user_id: int, 
        team_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        检查用户是否超过配额
        
        Returns:
            (是否允许, 错误消息)
        """
        quota = cls.get_effective_quota(db, user_id, team_id)
        today_usage = cls.get_today_usage(db, user_id)
        month_usage = cls.get_month_usage(db, user_id)
        
        # 检查每日请求数
        if today_usage.request_count >= quota['requests_per_day']:
            return False, f"今日 API 调用次数已达上限 ({quota['requests_per_day']} 次)"
        
        # 检查每月请求数
        if month_usage['request_count'] >= quota['requests_per_month']:
            return False, f"本月 API 调用次数已达上限 ({quota['requests_per_month']} 次)"
        
        # 检查每日 token
        if today_usage.total_tokens >= quota['tokens_per_day']:
            return False, f"今日 Token 使用量已达上限 ({quota['tokens_per_day']})"
        
        # 检查每月 token
        if month_usage['total_tokens'] >= quota['tokens_per_month']:
            return False, f"本月 Token 使用量已达上限 ({quota['tokens_per_month']})"
        
        # 检查每日费用
        if today_usage.total_cost >= quota['cost_per_day']:
            return False, f"今日费用已达上限 (${quota['cost_per_day']:.2f})"
        
        # 检查每月费用
        if month_usage['total_cost'] >= quota['cost_per_month']:
            return False, f"本月费用已达上限 (${quota['cost_per_month']:.2f})"
        
        return True, None
    
    @classmethod
    def record_usage(
        cls,
        db: Session,
        user_id: int,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        model: str,
        team_id: Optional[int] = None
    ):
        """记录 API 使用"""
        usage = cls.get_today_usage(db, user_id)
        
        # 更新使用量
        usage.request_count += 1
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens
        usage.total_tokens += input_tokens + output_tokens
        usage.total_cost += cost
        usage.team_id = team_id
        usage.updated_at = datetime.utcnow()
        
        # 更新模型使用详情
        model_usage = {}
        if usage.model_usage:
            try:
                model_usage = json.loads(usage.model_usage)
            except:
                pass
        
        if model not in model_usage:
            model_usage[model] = {'count': 0, 'tokens': 0, 'cost': 0.0}
        
        model_usage[model]['count'] += 1
        model_usage[model]['tokens'] += input_tokens + output_tokens
        model_usage[model]['cost'] += cost
        
        usage.model_usage = json.dumps(model_usage)
        
        db.add(usage)
        db.commit()
    
    @classmethod
    def get_quota_status(cls, db: Session, user_id: int, team_id: Optional[int] = None) -> Dict:
        """获取配额状态（配额 + 使用量 + 剩余）"""
        quota = cls.get_effective_quota(db, user_id, team_id)
        today_usage = cls.get_today_usage(db, user_id)
        month_usage = cls.get_month_usage(db, user_id)
        
        # 计算剩余
        remaining_requests_today = max(0, quota['requests_per_day'] - today_usage.request_count)
        remaining_tokens_today = max(0, quota['tokens_per_day'] - today_usage.total_tokens)
        remaining_cost_today = max(0, quota['cost_per_day'] - today_usage.total_cost)
        
        remaining_requests_month = max(0, quota['requests_per_month'] - month_usage['request_count'])
        remaining_tokens_month = max(0, quota['tokens_per_month'] - month_usage['total_tokens'])
        remaining_cost_month = max(0, quota['cost_per_month'] - month_usage['total_cost'])
        
        # 计算百分比
        usage_percent_requests = (month_usage['request_count'] / quota['requests_per_month'] * 100) if quota['requests_per_month'] > 0 else 0
        usage_percent_tokens = (month_usage['total_tokens'] / quota['tokens_per_month'] * 100) if quota['tokens_per_month'] > 0 else 0
        usage_percent_cost = (month_usage['total_cost'] / quota['cost_per_month'] * 100) if quota['cost_per_month'] > 0 else 0
        
        return {
            'quota': quota,
            'today_requests': today_usage.request_count,
            'today_tokens': today_usage.total_tokens,
            'today_cost': today_usage.total_cost,
            'month_requests': month_usage['request_count'],
            'month_tokens': month_usage['total_tokens'],
            'month_cost': month_usage['total_cost'],
            'remaining_requests_today': remaining_requests_today,
            'remaining_tokens_today': remaining_tokens_today,
            'remaining_cost_today': remaining_cost_today,
            'remaining_requests_month': remaining_requests_month,
            'remaining_tokens_month': remaining_tokens_month,
            'remaining_cost_month': remaining_cost_month,
            'usage_percent_requests': round(usage_percent_requests, 2),
            'usage_percent_tokens': round(usage_percent_tokens, 2),
            'usage_percent_cost': round(usage_percent_cost, 2),
        }
    
    @classmethod
    def set_user_quota(
        cls,
        db: Session,
        user_id: int,
        **kwargs
    ) -> ApiQuota:
        """设置用户配额"""
        quota = cls.get_user_quota(db, user_id)
        
        if not quota:
            quota = ApiQuota(
                quota_type=QuotaType.USER,
                target_id=user_id,
                **{k: v for k, v in kwargs.items() if v is not None}
            )
        else:
            for key, value in kwargs.items():
                if value is not None and hasattr(quota, key):
                    setattr(quota, key, value)
            quota.updated_at = datetime.utcnow()
        
        db.add(quota)
        db.commit()
        db.refresh(quota)
        
        return quota
    
    @classmethod
    def set_team_quota(
        cls,
        db: Session,
        team_id: int,
        **kwargs
    ) -> ApiQuota:
        """设置团队配额"""
        quota = cls.get_team_quota(db, team_id)
        
        if not quota:
            quota = ApiQuota(
                quota_type=QuotaType.TEAM,
                target_id=team_id,
                **{k: v for k, v in kwargs.items() if v is not None}
            )
        else:
            for key, value in kwargs.items():
                if value is not None and hasattr(quota, key):
                    setattr(quota, key, value)
            quota.updated_at = datetime.utcnow()
        
        db.add(quota)
        db.commit()
        db.refresh(quota)
        
        return quota


# 全局实例
quota_service = QuotaService()
