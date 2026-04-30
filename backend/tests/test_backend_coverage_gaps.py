"""关键后端回归缺口测试"""
import pytest
from httpx import AsyncClient
from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models.prompt import Prompt
from app.models.prompt_version import PromptVersion
from app.models.test_suite import PromptTestRun, PromptTestSuite
from app.models.user import User


async def get_token(client: AsyncClient, username: str, password: str) -> str:
    response = await client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    data = response.json()
    return (data.get("data") or {}).get("access_token", "")


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def owner_user(db_session: Session):
    user = User(
        username="owneruser",
        email="owner@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session: Session):
    user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session):
    user = User(
        username="adminuser",
        email="admin@example.com",
        hashed_password=get_password_hash("testpassword123"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def owner_prompt(db_session: Session, owner_user: User):
    prompt = Prompt(
        user_id=owner_user.id,
        title="Owner Prompt",
        content="Return a helpful answer for {{topic}}.",
        description="Private owner prompt",
        tags=["coverage"],
        is_public=False,
        version=1,
    )
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)

    version = PromptVersion(
        prompt_id=prompt.id,
        version=1,
        title=prompt.title,
        content=prompt.content,
        description=prompt.description,
        change_summary="初始版本",
    )
    db_session.add(version)
    db_session.commit()
    return prompt


@pytest.mark.asyncio
async def test_private_prompt_rejects_other_user_read_and_write(
    client: AsyncClient,
    owner_prompt: Prompt,
    other_user: User,
):
    token = await get_token(client, "otheruser", "testpassword123")

    read_response = await client.get(
        f"/api/prompt/{owner_prompt.id}",
        headers=auth_headers(token),
    )
    assert read_response.status_code == 200
    assert read_response.json()["code"] != 0

    update_response = await client.put(
        f"/api/prompt/{owner_prompt.id}",
        headers=auth_headers(token),
        json={"title": "stolen"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["code"] != 0


@pytest.mark.asyncio
async def test_prompt_content_update_creates_new_version(
    client: AsyncClient,
    db_session: Session,
    owner_prompt: Prompt,
):
    token = await get_token(client, "owneruser", "testpassword123")

    response = await client.put(
        f"/api/prompt/{owner_prompt.id}",
        headers=auth_headers(token),
        json={"content": "Updated content for {{topic}}."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["version"] == 2

    versions = db_session.exec(
        select(PromptVersion)
        .where(PromptVersion.prompt_id == owner_prompt.id)
        .order_by(PromptVersion.version)
    ).all()
    assert [version.version for version in versions] == [1, 2]
    assert versions[-1].content == "Updated content for {{topic}}."


@pytest.mark.asyncio
async def test_non_admin_cannot_access_admin_and_admin_quota_endpoints(
    client: AsyncClient,
    owner_user: User,
):
    token = await get_token(client, "owneruser", "testpassword123")

    admin_response = await client.get(
        "/api/admin/users",
        headers=auth_headers(token),
    )
    assert admin_response.status_code == 403

    quota_response = await client.get(
        "/api/quota/admin/list",
        headers=auth_headers(token),
    )
    assert quota_response.status_code == 403


@pytest.mark.asyncio
async def test_admin_user_can_access_admin_users(
    client: AsyncClient,
    admin_user: User,
):
    token = await get_token(client, "adminuser", "testpassword123")

    response = await client.get(
        "/api/admin/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["code"] == 0


@pytest.mark.asyncio
async def test_create_update_and_list_prompt_test_suite(
    client: AsyncClient,
    owner_prompt: Prompt,
):
    token = await get_token(client, "owneruser", "testpassword123")

    create_response = await client.post(
        "/api/test-suite",
        headers=auth_headers(token),
        json={
            "prompt_id": owner_prompt.id,
            "name": "Smoke suite",
            "suite_type": "smoke",
            "auto_run_on_save": True,
            "test_cases": [
                {
                    "name": "keyword check",
                    "variables": {"topic": "testing"},
                    "required_keywords": ["ok"],
                    "forbidden_keywords": ["error"],
                }
            ],
        },
    )
    assert create_response.status_code == 200
    create_data = create_response.json()
    assert create_data["code"] == 0
    suite_id = create_data["data"]["id"]
    assert create_data["data"]["auto_run_on_save"] is True

    update_response = await client.put(
        f"/api/test-suite/{suite_id}",
        headers=auth_headers(token),
        json={"name": "Full regression", "suite_type": "full"},
    )
    assert update_response.status_code == 200
    update_data = update_response.json()
    assert update_data["code"] == 0
    assert update_data["data"]["name"] == "Full regression"
    assert update_data["data"]["suite_type"] == "full"

    list_response = await client.get(
        f"/api/test-suite/prompt/{owner_prompt.id}",
        headers=auth_headers(token),
    )
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["code"] == 0
    assert [suite["id"] for suite in list_data["data"]] == [suite_id]


@pytest.mark.asyncio
async def test_invalid_prompt_test_suite_type_is_rejected(
    client: AsyncClient,
    owner_prompt: Prompt,
):
    token = await get_token(client, "owneruser", "testpassword123")

    response = await client.post(
        "/api/test-suite",
        headers=auth_headers(token),
        json={
            "prompt_id": owner_prompt.id,
            "name": "Bad suite",
            "suite_type": "nightly",
            "test_cases": [],
        },
    )

    assert response.status_code == 200
    assert response.json()["code"] != 0


@pytest.mark.asyncio
async def test_other_user_cannot_manage_private_prompt_test_suite(
    client: AsyncClient,
    db_session: Session,
    owner_prompt: Prompt,
    owner_user: User,
    other_user: User,
):
    suite = PromptTestSuite(
        user_id=owner_user.id,
        prompt_id=owner_prompt.id,
        name="Private suite",
        suite_type="smoke",
        test_cases=[],
    )
    db_session.add(suite)
    db_session.commit()
    db_session.refresh(suite)

    token = await get_token(client, "otheruser", "testpassword123")

    list_response = await client.get(
        f"/api/test-suite/prompt/{owner_prompt.id}",
        headers=auth_headers(token),
    )
    assert list_response.status_code == 200
    assert list_response.json()["code"] != 0

    update_response = await client.put(
        f"/api/test-suite/{suite.id}",
        headers=auth_headers(token),
        json={"name": "changed"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["code"] != 0


@pytest.mark.asyncio
async def test_run_prompt_test_suite_with_mocked_runner(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    owner_prompt: Prompt,
):
    async def fake_chat_completion(**kwargs):
        assert "testing" in kwargs["prompt"]
        return {"output": "ok result", "total_tokens": 12, "cost": 0.01}

    monkeypatch.setattr(
        "app.services.test_runner_service.OpenAIService.chat_completion",
        fake_chat_completion,
    )

    token = await get_token(client, "owneruser", "testpassword123")
    create_response = await client.post(
        "/api/test-suite",
        headers=auth_headers(token),
        json={
            "prompt_id": owner_prompt.id,
            "name": "Runnable suite",
            "suite_type": "smoke",
            "test_cases": [
                {
                    "name": "mocked case",
                    "variables": {"topic": "testing"},
                    "required_keywords": ["ok"],
                    "forbidden_keywords": ["error"],
                    "expected_output": "result",
                }
            ],
        },
    )
    suite_id = create_response.json()["data"]["id"]

    run_response = await client.post(
        f"/api/test-suite/{suite_id}/run",
        headers=auth_headers(token),
        json={"candidate_version": 1, "enable_evaluation": False},
    )

    assert run_response.status_code == 200
    run_data = run_response.json()
    assert run_data["code"] == 0
    assert run_data["data"]["status"] == "completed"
    assert run_data["data"]["summary"]["passed_cases"] == 1
    assert run_data["data"]["summary"]["failed_cases"] == 0
    assert run_data["data"]["results"][0]["passed"] is True

    detail_response = await client.get(
        f"/api/test-suite/runs/{run_data['data']['id']}",
        headers=auth_headers(token),
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["summary"]["pass_rate"] == 100

    runs_response = await client.get(
        f"/api/test-suite/runs?prompt_id={owner_prompt.id}&suite_id={suite_id}",
        headers=auth_headers(token),
    )
    assert runs_response.status_code == 200
    assert runs_response.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_prompt_test_suite_run_records_failed_status_for_missing_version(
    client: AsyncClient,
    db_session: Session,
    owner_prompt: Prompt,
    owner_user: User,
):
    suite = PromptTestSuite(
        user_id=owner_user.id,
        prompt_id=owner_prompt.id,
        name="Missing version suite",
        suite_type="smoke",
        test_cases=[{"name": "will fail"}],
    )
    db_session.add(suite)
    db_session.commit()
    db_session.refresh(suite)

    token = await get_token(client, "owneruser", "testpassword123")
    response = await client.post(
        f"/api/test-suite/{suite.id}/run",
        headers=auth_headers(token),
        json={"candidate_version": 999, "enable_evaluation": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["status"] == "failed"
    assert "Prompt 版本不存在" in data["data"]["error"]

    run = db_session.get(PromptTestRun, data["data"]["id"])
    assert run.status == "failed"
