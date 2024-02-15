from httpx import AsyncClient


async def test_valid_room_creation(ac: AsyncClient):
    # Login
    login_data = {
        "username": "gelo21region",
        "password": "string1"
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
    room_data = {"room_name": "string"}
    post_room_response = await ac.post("/api/room", headers=headers, json=room_data)
    assert post_room_response.status_code == 200
    assert post_room_response.json()["room_name"] == "string"
