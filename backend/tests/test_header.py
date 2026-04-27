"""全面API测试脚本 - 测试所有API接口"""
import pytest
import pytest_asyncio
import uuid
from datetime import datetime
from httpx import AsyncClient
from sqlmodel import Session, select
from app.main import app
from app.core.database import engine, get_session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.prompt import Prompt, UserPromptFavorite
from app.models.prompt_version import PromptVersion
from app.models.team import Team, TeamMember, TeamPrompt
from app.models.template import PromptTemplate, TemplateCategory
from app.models.ai_config import AIConfig

# 配置 pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


# ==================== 辅助函数 ====================

def generate_unique_username():
    """生成唯一的用户名"""
    return f"testuser_{uuid.uuid4().hex[:8]}"


def generate_unique_email():
    """生成唯一的邮箱"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


async def login_and_get_token(client: AsyncClient, username: str, password: str) -> str:
    """登录并获取token"""
    response = await client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        json_data = response.json()
        if json_data and json_data.get("code") == 0:
            return json_data.get("data", {}).get("access_token", "")
    return ""


async def login_as(client: AsyncClient, user) -> str:
    """使用 user 对象凭证登录"""
    if hasattr(user, 'credentials'):
        return await login_and_get_token(client, user.credentials['username'], user.credentials['password'])
    return ""


async def get_auth_headers(client: AsyncClient, username: str, password: str) -> dict:
    """获取认证头"""
    token = await login_and_get_token(client, username, password)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

