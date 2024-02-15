import pytest
from httpx import AsyncClient


# Register
@pytest.mark.parametrize("email, username, password", [
    ("popov.gleb.01@mail.ru", "gelo21region", "string1"),
    ("popov.gleb.02@mail.ru", "gelo121region", "string1"),
    ("popov.gleb@mail.ru", "gelo123g", "string1"),
    ("popov@mail.ru", "four123f", "string1"),
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


@pytest.mark.parametrize("username, password", [
    ("gelo21region", "string1")
])
async def test_valid_user_login(username, password, ac: AsyncClient):
    user_data = {
        "username": username,
        "password": password
    }
    response = await ac.post("/api/auth/jwt/login", data=user_data)
    assert response.status_code == 200


# #  Logout
# @pytest.mark.parametrize("username, password", [
#     ("gelo21region", "string1")
# ])
# async def test_valid_user_logout(username, password, ac: AsyncClient):
#     user_data = {
#         "username": username,
#         "password": password
#     }
#     login_response = await ac.post("/api/auth/jwt/login", data=user_data)
#     assert login_response.status_code == 200
#     assert "access_token" in login_response.json()
#     assert "token_type" in login_response.json()
#
#     token = login_response.json()['access_token']
#
#     headers = {
#         "Accept": "application/json",
#         "Authorization": "Bearer " + token
#     }
#     response = await ac.post(
#         "/api/auth/jwt/logout",
#         headers=headers
#     )
#     assert response.status_code == 200
