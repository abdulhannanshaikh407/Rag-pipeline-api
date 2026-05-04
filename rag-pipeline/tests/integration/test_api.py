import pytest
from httpx import AsyncClient

async def test_health(client: AsyncClient):
    """Test the health endpoint returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

async def test_root(client: AsyncClient):
    """Test the root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"

async def test_register_and_login(client: AsyncClient):
    """Test user registration and login flow."""
    response = await client.post(
        "/auth/register",
        json={"username": "testuser2", "email": "test2@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser2"
    assert "api_key" in data

    # Login
    response = await client.post(
        "/auth/token",
        data={"username": "testuser2", "password": "password123"}
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

async def test_duplicate_registration(client: AsyncClient, registered_user):
    """Test that duplicate registration fails."""
    response = await client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 400

async def test_unauthorized_query(client: AsyncClient):
    """Test that query without auth returns 401."""
    response = await client.post(
        "/query",
        json={"question": "What is AI?"}
    )
    assert response.status_code == 401

async def test_authorized_query_with_token(registered_user, client: AsyncClient):
    """Test that query with valid token works (will fail on LLM but auth passes)."""
    token = registered_user["token"]
    response = await client.post(
        "/query",
        json={"question": "What is AI?", "stream": False},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code != 401

async def test_authorized_query_with_api_key(registered_user, client: AsyncClient):
    """Test that query with API key works."""
    api_key = registered_user["api_key"]
    response = await client.post(
        "/query",
        json={"question": "What is AI?", "stream": False},
        headers={"X-API-Key": api_key}
    )
    assert response.status_code != 401
