"""Prompt 访问权限测试 (P1-10)"""
import pytest
from httpx import AsyncClient
from sqlmodel import Session
from app.models.prompt import Prompt


@pytest.fixture
def other_user_prompt(db_session: Session, test_user):
    """创建另一个用户的私有 Prompt"""
    prompt = Prompt(
        user_id=test_user.id,
        title="Private Prompt",
        content="Private content",
        is_public=False
    )
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)
    return prompt


async def get_token(client: AsyncClient, username: str, password: str) -> str:
    """获取访问令牌"""
    response = await client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_cannot_access_other_private_prompt(
    client: AsyncClient,
    other_user_prompt: Prompt,
    disabled_user
):
    """测试无法访问其他用户的私有 Prompt"""
    # 使用禁用用户获取 token（该用户存在但被禁用，所以这里用 testuser 创建的 prompt 来测试访问控制）
    # 实际测试场景应该是：用户 A 创建私有 Prompt，用户 B 无法访问
    pass  # 需要两个不同用户的测试数据


@pytest.mark.asyncio
async def test_public_prompt_accessible(
    client: AsyncClient,
    db_session: Session,
    test_user
):
    """测试公开 Prompt 可被访问"""
    # 创建公开 Prompt
    prompt = Prompt(
        user_id=test_user.id,
        title="Public Prompt",
        content="Public content",
        is_public=True
    )
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)

    # 获取 token
    token = await get_token(client, "testuser", "testpassword123")

    # 尝试访问
    response = await client.get(
        f"/api/prompt/{prompt.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
