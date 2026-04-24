"""测试配置"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, Session
from app.main import app
from app.core.database import engine, get_session
from app.core.security import get_password_hash
from app.models.user import User


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
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
