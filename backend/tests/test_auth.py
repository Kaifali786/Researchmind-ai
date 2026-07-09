import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration endpoint with valid data."""
    payload = {
        "email": "tester@example.com",
        "username": "tester",
        "password": "supersecurepassword123",
        "full_name": "Test User"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == "tester@example.com"
    assert data["username"] == "tester"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data  # Ensure security constraints


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient):
    """Test that duplicate registrations fail with a 409 status code."""
    payload = {
        "email": "dupe@example.com",
        "username": "dupe",
        "password": "password123",
        "full_name": "Dupe User"
    }
    
    # First registration
    response1 = await client.post("/api/v1/auth/register", json=payload)
    assert response1.status_code == 201

    # Second registration with same email
    response2 = await client.post("/api/v1/auth/register", json=payload)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test user login returns a JWT access token."""
    # 1. Register first
    payload = {
        "email": "login_test@example.com",
        "username": "login_test",
        "password": "password123",
        "full_name": "Login Test"
    }
    await client.post("/api/v1/auth/register", json=payload)

    # 2. Try logging in
    login_payload = {
        "email": "login_test@example.com",
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"



@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient):
    """Test retrieving authenticated user profile using token header."""
    # 1. Register & Login
    payload = {
        "email": "profile_test@example.com",
        "username": "profile_test",
        "password": "password123",
        "full_name": "Profile Test"
    }
    await client.post("/api/v1/auth/register", json=payload)

    login_payload = {
        "email": "profile_test@example.com",
        "password": "password123"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    token = login_res.json()["access_token"]

    # 2. Get profile with Auth header
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == "profile_test@example.com"
    assert data["username"] == "profile_test"
