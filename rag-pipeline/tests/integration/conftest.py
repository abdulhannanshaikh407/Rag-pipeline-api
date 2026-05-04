import pytest
import pytest_asyncio
from httpx import AsyncClient
try:
    from httpx import ASGITransport
except ImportError:
    from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_temp.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="module")
async def test_db():
    """Provide a test database session."""
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="module")
async def client(test_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture(scope="module")
async def registered_user(client):
    """Register a test user and return user data with token."""
    response = await client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    user_data = response.json()

    # Get token
    token_response = await client.post(
        "/auth/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert token_response.status_code == 200
    token_data = token_response.json()

    return {
        "user": user_data,
        "token": token_data["access_token"],
        "api_key": user_data["api_key"]
    }
