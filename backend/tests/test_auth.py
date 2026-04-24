"""认证相关测试"""
import pytest
from httpx import AsyncClient
from sqlmodel import Session


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """测试登录成功"""
    response = await client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["data"]["user"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """测试登录失败 - 密码错误"""
    response = await client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient):
    """测试登录失败 - 用户不存在"""
    response = await client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """测试注册成功"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["data"]["user"]["username"] == "newuser"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    """测试注册失败 - 用户名重复"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
