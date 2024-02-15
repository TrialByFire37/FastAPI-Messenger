import pytest
from httpx import AsyncClient


# Register
@pytest.mark.parametrize("email, username, password", [
    ("popov.gleb.01@mail.ru", "gelo21region", "string1"),
])
async def test_valid_user_registration(email, username, password, ac: AsyncClient):
    user_data = {
        "email": email,
        "password": password,
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": username
    }
    response = await ac.post("/api/register", json=user_data)
    assert response.status_code == 201


@pytest.mark.parametrize("email, username, password", [
    ("popov.gleb@mail.ru", "demon666", "string1"),
])
async def test_valid_user_registration_2(email, username, password, ac: AsyncClient):
    user_data = {
        "email": email,
        "password": password,
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": username
    }
    response = await ac.post("/api/register", json=user_data)
    assert response.status_code == 201
