from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel import Session, select
from .database import get_session
from .security import decode_access_token
from ..models.user import User

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话依赖"""
    yield from get_session()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    print(f"[AUTH] 收到 Token: {token[:50]}...")
    
    payload = decode_access_token(token)
    print(f"[AUTH] Token 解码结果: {payload}")
    
    if payload is None:
        print("[ERROR] Token 解码失败！")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )
    
    user_id_str: Optional[str] = payload.get("sub")
    print(f"[AUTH] 从 Token 中提取的 user_id (字符串): {user_id_str}")
    
    if user_id_str is None:
        print("[ERROR] Token 中没有 sub 字段！")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )
    
    try:
        user_id = int(user_id_str)
        print(f"[AUTH] 转换为整数的 user_id: {user_id}")
    except ValueError:
        print(f"[ERROR] user_id 转换失败: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )
    
    user = db.get(User, user_id)
    print(f"[AUTH] 从数据库查询到的用户: {user}")
    
    if user is None:
        print(f"[ERROR] 数据库中找不到 user_id={user_id} 的用户！")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    print(f"[OK] 用户验证成功: {user.username}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


# 别名函数，方便使用
require_admin = get_current_admin_user