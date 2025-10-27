"""访问控制中间件 - IP白名单、频率限制"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import time
from collections import defaultdict
from datetime import datetime, timedelta


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP白名单中间件"""
    
    def __init__(self, app, whitelist: Optional[list] = None, enabled: bool = False):
        super().__init__(app)
        self.whitelist = set(whitelist or [])
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 检查白名单
        if client_ip not in self.whitelist:
            return JSONResponse(
                status_code=403,
                content={
                    "code": 403,
                    "message": "访问被拒绝：IP地址不在白名单中",
                    "data": None
                }
            )
        
        return await call_next(request)
    
    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """获取真实客户端IP"""
        # 考虑代理服务器
        if 'x-forwarded-for' in request.headers:
            return request.headers['x-forwarded-for'].split(',')[0].strip()
        elif 'x-real-ip' in request.headers:
            return request.headers['x-real-ip']
        elif request.client:
            return request.client.host
        return '0.0.0.0'


class RateLimitMiddleware(BaseHTTPMiddleware):
    """频率限制中间件"""
    
    def __init__(
        self, 
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        enabled: bool = True
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.enabled = enabled
        
        # 存储请求记录 {ip: [(timestamp, count)]}
        self.minute_requests = defaultdict(list)
        self.hour_requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # 排除OPTIONS预检请求（CORS）
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # 获取客户端IP
        client_ip = IPWhitelistMiddleware._get_client_ip(request)
        
        # 排除某些路径（如健康检查、静态资源）
        # 使用 request.url.path 而不是 request.path
        request_path = str(request.url.path) if hasattr(request, 'url') else '/'
        if self._is_excluded_path(request_path):
            return await call_next(request)
        
        # 检查频率限制
        now = time.time()
        
        # 清理过期记录
        self._cleanup_old_records(client_ip, now)
        
        # 检查分钟级限制
        minute_count = len([
            ts for ts in self.minute_requests[client_ip]
            if now - ts < 60
        ])
        
        if minute_count >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "code": 429,
                    "message": f"请求过于频繁，每分钟限制{self.requests_per_minute}次请求",
                    "data": {
                        "limit": self.requests_per_minute,
                        "window": "1分钟",
                        "retry_after": 60
                    }
                }
            )
        
        # 检查小时级限制
        hour_count = len([
            ts for ts in self.hour_requests[client_ip]
            if now - ts < 3600
        ])
        
        if hour_count >= self.requests_per_hour:
            return JSONResponse(
                status_code=429,
                content={
                    "code": 429,
                    "message": f"请求过于频繁，每小时限制{self.requests_per_hour}次请求",
                    "data": {
                        "limit": self.requests_per_hour,
                        "window": "1小时",
                        "retry_after": 3600
                    }
                }
            )
        
        # 记录请求
        self.minute_requests[client_ip].append(now)
        self.hour_requests[client_ip].append(now)
        
        # 添加rate limit headers
        response = await call_next(request)
        response.headers['X-RateLimit-Limit-Minute'] = str(self.requests_per_minute)
        response.headers['X-RateLimit-Limit-Hour'] = str(self.requests_per_hour)
        response.headers['X-RateLimit-Remaining-Minute'] = str(
            max(0, self.requests_per_minute - minute_count - 1)
        )
        response.headers['X-RateLimit-Remaining-Hour'] = str(
            max(0, self.requests_per_hour - hour_count - 1)
        )
        
        return response
    
    def _cleanup_old_records(self, client_ip: str, now: float):
        """清理过期记录"""
        # 清理1分钟前的记录
        self.minute_requests[client_ip] = [
            ts for ts in self.minute_requests[client_ip]
            if now - ts < 60
        ]
        
        # 清理1小时前的记录
        self.hour_requests[client_ip] = [
            ts for ts in self.hour_requests[client_ip]
            if now - ts < 3600
        ]
        
        # 清理空记录
        if not self.minute_requests[client_ip]:
            del self.minute_requests[client_ip]
        if not self.hour_requests[client_ip]:
            del self.hour_requests[client_ip]
    
    @staticmethod
    def _is_excluded_path(path: str) -> bool:
        """判断路径是否排除在频率限制之外"""
        excluded_paths = [
            '/health',
            '/docs',
            '/redoc',
            '/openapi.json',
            '/static/',
        ]
        
        return any(path.startswith(excluded) for excluded in excluded_paths)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 添加安全响应头
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 获取客户端信息
        client_ip = IPWhitelistMiddleware._get_client_ip(request)
        user_agent = request.headers.get('user-agent', 'Unknown')
        request_path = str(request.url.path) if hasattr(request, 'url') else '/'
        request_method = request.method if hasattr(request, 'method') else 'UNKNOWN'
        
        # 处理请求
        status_code = 200
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise
        finally:
            # 计算请求时间
            process_time = time.time() - start_time
            
            # 记录日志（简单打印，实际应该记录到日志系统）
            log_message = (
                f"[{datetime.now().isoformat()}] "
                f"{request_method} {request_path} "
                f"- IP: {client_ip} "
                f"- Status: {status_code} "
                f"- Time: {process_time:.3f}s"
            )
            
            # 高延迟警告
            if process_time > 5.0:
                log_message += " [SLOW]"
            
            print(log_message)
        
        return response

