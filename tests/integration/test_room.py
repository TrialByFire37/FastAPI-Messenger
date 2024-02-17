import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("username, password, room_name", [
    ("gelo121region", "string1", "aaaa"),
    ("gelo123g", "string1", "bbbb"),
])
async def test_valid_room_creation(username, password, room_name, ac: AsyncClient):
    # Login
    login_data = {
        "username": username,
        "password": password
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    # Создание комнаты
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    room_data = {"room_name": room_name}
    post_room_response = await ac.post("/api/room", headers=headers, json=room_data)
    assert post_room_response.status_code == 200
    assert post_room_response.json()["room_name"] == room_name
