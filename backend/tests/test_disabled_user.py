"""禁用用户权限测试 (P0-5)"""
import pytest
from httpx import AsyncClient
from sqlmodel import Session


async def get_token(client: AsyncClient, username: str, password: str) -> str:
    """获取访问令牌"""
    response = await client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    data = response.json()
    return (data.get("data") or {}).get("access_token", "")


@pytest.mark.asyncio
async def test_disabled_user_cannot_access_protected_endpoints(
    client: AsyncClient,
    disabled_user
):
    """测试被禁用的用户无法访问受保护接口"""
    # 禁用用户无法登录获取 token
    token = await get_token(client, "disableduser", "testpassword123")
    assert token == ""

    # 即使没有有效 token，也不能访问受保护接口

    # 尝试访问受保护接口（如获取 Prompt 列表）
    response = await client.get(
        "/api/prompt/list",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [401, 403]
    data = response.json()
    assert data.get("detail")


@pytest.mark.asyncio
async def test_active_user_can_access_protected_endpoints(
    client: AsyncClient,
    test_user
):
    """测试正常用户可以访问受保护接口"""
    # 获取 token
    token = await get_token(client, "testuser", "testpassword123")

    # 访问受保护接口
    response = await client.get(
        "/api/prompt/list",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 应该返回 200
    assert response.status_code == 200
