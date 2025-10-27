import time
from typing import Dict, Optional
from datetime import datetime, timedelta


class RateLimitService:
    """
    频率限制服务
    用于防止 API 滥用
    """
    
    def __init__(self):
        # 存储用户的请求记录 {user_id: [timestamps]}
        self._requests: Dict[int, list] = {}
        
        # 配置
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000
        self.max_requests_per_day = 10000
    
    def check_rate_limit(self, user_id: int) -> tuple[bool, Optional[str]]:
        """
        检查用户是否超过频率限制
        
        Args:
            user_id: 用户ID
        
        Returns:
            (是否允许, 错误消息)
        """
        now = time.time()
        
        # 初始化用户记录
        if user_id not in self._requests:
            self._requests[user_id] = []
        
        # 清理过期记录（超过24小时）
        self._requests[user_id] = [
            ts for ts in self._requests[user_id]
            if now - ts < 86400  # 24小时
        ]
        
        timestamps = self._requests[user_id]
        
        # 检查每分钟限制
        minute_ago = now - 60
        recent_minute = [ts for ts in timestamps if ts > minute_ago]
        if len(recent_minute) >= self.max_requests_per_minute:
            return False, f"每分钟请求次数超限（{self.max_requests_per_minute}次）"
        
        # 检查每小时限制
        hour_ago = now - 3600
        recent_hour = [ts for ts in timestamps if ts > hour_ago]
        if len(recent_hour) >= self.max_requests_per_hour:
            return False, f"每小时请求次数超限（{self.max_requests_per_hour}次）"
        
        # 检查每天限制
        day_ago = now - 86400
        recent_day = [ts for ts in timestamps if ts > day_ago]
        if len(recent_day) >= self.max_requests_per_day:
            return False, f"每天请求次数超限（{self.max_requests_per_day}次）"
        
        return True, None
    
    def record_request(self, user_id: int):
        """记录一次请求"""
        now = time.time()
        
        if user_id not in self._requests:
            self._requests[user_id] = []
        
        self._requests[user_id].append(now)
    
    def get_usage_stats(self, user_id: int) -> Dict:
        """获取用户的使用统计"""
        now = time.time()
        
        if user_id not in self._requests:
            return {
                "requests_last_minute": 0,
                "requests_last_hour": 0,
                "requests_last_day": 0,
            }
        
        timestamps = self._requests[user_id]
        
        minute_ago = now - 60
        hour_ago = now - 3600
        day_ago = now - 86400
        
        return {
            "requests_last_minute": len([ts for ts in timestamps if ts > minute_ago]),
            "requests_last_hour": len([ts for ts in timestamps if ts > hour_ago]),
            "requests_last_day": len([ts for ts in timestamps if ts > day_ago]),
            "limit_per_minute": self.max_requests_per_minute,
            "limit_per_hour": self.max_requests_per_hour,
            "limit_per_day": self.max_requests_per_day,
        }


# 全局实例
rate_limiter = RateLimitService()

