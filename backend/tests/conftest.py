"""测试配置"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core import database
from app.core.database import get_session
from app.core.security import get_password_hash
from app.models.user import User
from app.core.access_control import RateLimitMiddleware
from app.services import test_runner_service


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
database.engine = test_engine
test_runner_service.engine = test_engine
for middleware in app.user_middleware:
    if middleware.cls is RateLimitMiddleware:
        middleware.kwargs["enabled"] = False
app.middleware_stack = app.build_middleware_stack()

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    session = Session(test_engine)
    yield session
    session.close()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """创建测试客户端"""
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2(db_session: Session):
    """创建第二个测试用户"""
    user = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_prompt(db_session: Session, test_user):
    """创建测试Prompt"""
    from app.models.prompt import Prompt
    from app.models.prompt_version import PromptVersion

    prompt = Prompt(
        user_id=test_user.id,
        title="测试Prompt",
        content="这是一个测试用的Prompt内容",
        description="测试描述",
        tags=["test", "demo"],
        is_public=False,
        version=1
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
        change_summary="初始版本"
    )
    db_session.add(version)
    db_session.commit()

    return prompt


@pytest.fixture
def disabled_user(db_session: Session):
    """创建被禁用的用户"""
    user = User(
        username="disableduser",
        email="disabled@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
