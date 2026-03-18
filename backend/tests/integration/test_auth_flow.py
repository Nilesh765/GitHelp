import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.modules.user.model import User

pytestmark = pytest.mark.asyncio

async def test_register_creates_user(client: AsyncClient, db_session):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["email"] == "newuser@test.com"
    
    result = await db_session.execute(select(User).where(User.email == "newuser@test.com"))
    user = result.scalar_one_or_none()
    
    assert user is not None
    assert user.email == "newuser@test.com"
    assert user.hashed_password != "SecurePassword123!"

async def test_register_duplicate_email_returns_409(client: AsyncClient):
    payload = {"email": "duplicate@test.com", "password": "Password123!", "full_name": "Test User"}
    
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    
    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 400

async def test_login_returns_tokens(client: AsyncClient):
    payload = {"email": "logintest@test.com", "password": "Password123!", "full_name": "Test User"}
    await client.post("/api/v1/auth/register", json=payload)
    
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "logintest@test.com", "password": "Password123!"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

async def test_login_wrong_password_returns_401(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@test.com", "password": "CorrectPassword123!", "full_name": "Test User"}
    )
    
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpass@test.com", "password": "WrongPassword"}
    )
    assert response.status_code == 401

async def test_get_me_without_token_returns_401(client: AsyncClient):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401

async def test_get_me_with_valid_token_returns_user(auth_client):
    client, user = auth_client
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == user.email
    assert data["id"] == str(user.id)
    assert "hashed_password" not in data

async def test_refresh_token_rotation(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@test.com", "password": "Password123!", "full_name": "Test User"}
    )
    
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@test.com", "password": "Password123!"}
    )
    tokens = login.json()
    old_refresh_token = tokens["refresh_token"]
    
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token}
    )
    assert refresh_response.status_code == 200
    
    new_tokens = refresh_response.json()
    assert new_tokens["refresh_token"] != old_refresh_token
    
    second_attempt = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token}
    )
    assert second_attempt.status_code == 401