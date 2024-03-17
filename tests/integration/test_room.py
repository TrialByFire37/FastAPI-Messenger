import pytest
from httpx import AsyncClient


# todo: (14) Тест успешного создания комнаты
@pytest.mark.parametrize("username, password, room_name", [
    ("gelo121region", "string1", "aaaa"),
    ("gelo121region", "string1", "1234"),
    ("gelo121region", "string1", "3333"),
    ("gelo123g", "string1", "bbbb"),
])
async def test_valid_room_creation(username, password, room_name, ac: AsyncClient):
    login_data = {
        "username": username,
        "password": password
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    room_data = {"room_name": room_name}
    post_room_response = await ac.post("/api/room", headers=headers, json=room_data)
    assert post_room_response.status_code == 200


# todo: (15) Тест неудачного создания комнаты
@pytest.mark.parametrize("username, password, room_name", [
    ("gelo121region", "string1", "  "),
    ("gelo123g", "string1", " "),
])
async def test_room_create_validation_error(username, password, room_name, ac: AsyncClient):
    login_data = {
        "username": username,
        "password": password
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    room_data = {"room_name": room_name}
    post_room_response = await ac.post("/api/room", headers=headers, json=room_data)
    assert post_room_response.status_code == 422


# todo: (18) Тест успешного добавления пользователя в комнату
@pytest.mark.parametrize("username, password, room_name", [
    ("gelo123g", "string1", "aaaa"),
    ("gelo121region", "string1", "bbbb"),
])
async def test_valid_room_add(username, password, room_name, ac: AsyncClient):
    login_data = {
        "username": username,
        "password": password
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    post_room_response = await ac.put(url="/api/room/" + room_name, headers=headers)
    assert post_room_response.status_code == 200


# todo: (19) Тест успешного удаления комнаты
@pytest.mark.parametrize("username, password, room_name", [
    ("gelo121region", "string1", "1234"),
    ("gelo121region", "string1", "3333"),
])
async def test_valid_room_delete(username, password, room_name, ac: AsyncClient):
    login_data = {
        "username": username,
        "password": password
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    post_room_response = await ac.delete(url="/api/room/" + room_name, headers=headers)
    assert post_room_response.status_code == 200


# todo: (20) Тест неудачного удаления комнаты
# @pytest.mark.parametrize("username, password, room_name", [
#     ("gelo121region", "string1", " "),
#     ("gelo121region", "string1", "  "),
# ])
# async def test_room_delete_validation_error(username, password, room_name, ac: AsyncClient):
#     # Login
#     login_data = {
#         "username": username,
#         "password": password
#     }
#     login_response = await ac.post("/api/auth/jwt/login", data=login_data)
#     assert login_response.status_code == 200
#     assert "access_token" in login_response.json()
#     assert "token_type" in login_response.json()
#
#     token = login_response.json()['access_token']
#
#     # Создание комнаты
#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#         "Authorization": "Bearer " + token,
#     }
#     post_room_response = await ac.delete(url="/api/room/" + room_name, headers=headers)
#     assert post_room_response.status_code == 422


# todo: (21) Тест создание и последующего удаления комнаты
@pytest.mark.parametrize("username, password, room_name", [
    ("gelo121region", "string1", "room_1"),
])
async def test_valid_room_create_and_delete(username, password, room_name, ac: AsyncClient):
    login_data = {
        "username": username,
        "password": password
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    room_data = {"room_name": room_name}
    post_room_response = await ac.post("/api/room", headers=headers, json=room_data)
    assert post_room_response.status_code == 200

    delete_room_response = await ac.delete(url="/api/room/" + room_name, headers=headers)
    assert delete_room_response.status_code == 200


#  todo: (24) Аутентификация пользователя и избранные комнаты:
@pytest.mark.parametrize("username, password, room_name", [
    ("gelo123g", "string1", "bbbb"),
])
async def test_auth_by_login_and_password_and_get_favorites_and_post_favorite(username, password, room_name,
                                                                              ac: AsyncClient):
    login_data = {
        "username": username,
        "password": password
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    get_favorites_response = await ac.get("/api/favorites?page=1&limit=10", headers=headers)
    assert get_favorites_response.status_code == 200

    list_favorites = get_favorites_response.json()

    post_favorite_data = {
        "room_name": room_name,
        "is_chosen": True
    }
    post_favorite_response = await ac.post("/api/favorite", headers=headers, json=post_favorite_data)
    assert post_favorite_response.status_code == 200

    get_favorites_response = await ac.get("/api/favorites?page=1&limit=10", headers=headers)
    assert get_favorites_response.status_code == 200
    assert len(get_favorites_response.json()) == len(list_favorites) + 1


#  todo: (29) Создание комнаты и добавление ее в избранное:
@pytest.mark.parametrize("username, password, room_name", [
    ("gelo123g", "string1", "pppp"),
])
async def test_get_room_by_name_and_put_user_in_room(username, password, room_name, ac: AsyncClient):
    login_data = {
        "username": username,
        "password": password
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    room_data = {"room_name": room_name}
    post_room_response = await ac.post("/api/room", headers=headers, json=room_data)
    assert post_room_response.status_code == 200

    post_favorite_data = {
        "room_name": room_name,
        "is_chosen": True
    }
    post_favorite_response = await ac.post("/api/favorite", headers=headers, json=post_favorite_data)
    assert post_favorite_response.status_code == 200

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    get_favorites_response = await ac.get("/api/favorites?page=1&limit=10", headers=headers)
    assert get_favorites_response.status_code == 200


#  todo: (30) Получение списка избранных комнат и удаление комнаты из избранного:
@pytest.mark.parametrize("username, password, room_name", [
    ("gelo123g", "string1", "pppp"),
])
async def test_get_favorites_and_delete_favorite(username, password, room_name,
                                                 ac: AsyncClient):
    login_data = {
        "username": username,
        "password": password
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }
    get_favorites_response = await ac.get("/api/favorites?page=1&limit=10", headers=headers)
    assert get_favorites_response.status_code == 200

    list_favorites = get_favorites_response.json()

    post_favorite_data = {
        "room_name": room_name,
        "is_chosen": False
    }
    post_favorite_response = await ac.post("/api/favorite", headers=headers, json=post_favorite_data)
    assert post_favorite_response.status_code == 200

    get_favorites_response = await ac.get("/api/favorites?page=1&limit=10", headers=headers)
    assert get_favorites_response.status_code == 200
    assert len(get_favorites_response.json()) == len(list_favorites) - 1
