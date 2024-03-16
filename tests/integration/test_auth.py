import pytest
from httpx import AsyncClient


# Register
@pytest.mark.parametrize("email, username, password", [
    ("popov.gleb.01@mail.ru", "gelo21region", "string1"),
    ("popov.gleb.02@mail.ru", "gelo121region", "string1"),
    ("popov.gleb@mail.ru", "gelo123g", "string1"),
    ("popov@mail.ru", "four123f", "string1"),
    ("nofavdude@mail.ru", "no_favorites_dude1", "stringi1"),
])
async def test_user_registration(email, username, password, ac: AsyncClient):
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


# todo: (1) Тест успешного входа
@pytest.mark.parametrize("username, password", [
    ("gelo121region", "string1"),
    ("gelo123g", "string1"),
])
async def test_user_login(username, password, ac: AsyncClient):
    user_data = {
        "username": username,
        "password": password
    }
    response = await ac.post("/api/auth/jwt/login", data=user_data)
    assert response.status_code == 200


# todo: (2) Тест неудачного входа с неправильным паролем
@pytest.mark.parametrize("username, password", [
    ("gelo121region", "string123"),
    ("gelo123g", "string123"),
])
async def test_user_login_wrong_password(username, password, ac: AsyncClient):
    user_data = {
        "username": username,
        "password": password
    }
    response = await ac.post("/api/auth/jwt/login", data=user_data)
    assert response.status_code == 400


# todo: (3) Тест неудачного входа с несуществующим именем пользователя
@pytest.mark.parametrize("username, password", [
    ("gelo11111", "string1"),
    ("gelo12", "string1"),
])
async def test_user_login_wrong_username(username, password, ac: AsyncClient):
    user_data = {
        "username": username,
        "password": password
    }
    response = await ac.post("/api/auth/jwt/login", data=user_data)
    assert response.status_code == 400


# todo: (4) Тест запроса восстановления пароля для существующего аккаунта
@pytest.mark.parametrize("email", [
    ("popov.gleb.01@mail.ru")
])
async def test_user_forgot_password(email, ac: AsyncClient):
    user_data = {
        "email": email
    }
    response = await ac.post("/api/auth/forgot-password", json=user_data)
    assert response.status_code == 202


# todo: (5) Тест запроса восстановления пароля для несуществующего аккаунта
@pytest.mark.parametrize("email", [
    ("popov.gleb.422@mail.ru")
])
async def test_user_forgot_password_validation_error(email, ac: AsyncClient):
    user_data = {
        "email": email
    }
    response = await ac.post("/api/auth/forgot-password", data=user_data)
    assert response.status_code == 422


# # todo: (6) Тест успешного восстановления пароля (Fail)
# @pytest.mark.parametrize("username, password, new_password", [
#     ("gelo121region", "string1", "string2"),
# ])
# async def test_user_password_reset(username, password, new_password, ac: AsyncClient):
#     user_data = {
#         "username": username,
#         "password": password
#     }
#     response = await ac.post("/api/auth/jwt/login", data=user_data)
#     assert response.status_code == 200
#     assert response.json()['access_token'] is not None
#
#     token = response.json()['access_token']
#
#     refresh_data = {
#         "token": token,
#         "password": new_password
#     }
#
#     response = await ac.post(url="/api/auth/reset-password", json=refresh_data)
#     assert response.status_code == 200


# todo: (7) Тест неудачного восстановления пароля
@pytest.mark.parametrize("token, new_password", [
    ("gelo121region", "new_password"),
])
async def test_user_password_reset_bad_request(token, new_password, ac: AsyncClient):
    refresh_data = {
        "token": token,
        "password": new_password
    }
    response = await ac.post(url="/api/auth/reset-password", json=refresh_data)
    assert response.status_code == 400


# todo: (8) Тест успешного получения информации о пользователе
@pytest.mark.parametrize("username, password", [
    ("gelo121region", "string1"),
])
async def test_user_me(username, password, ac: AsyncClient):
    user_data = {
        "username": username,
        "password": password
    }
    response = await ac.post("/api/auth/jwt/login", data=user_data)
    assert response.status_code == 200
    assert response.json()['access_token'] is not None

    token = response.json()['access_token']

    headers = {
        "Authorization": "Bearer " + token
    }
    response = await ac.get("/api/user/me", headers=headers)
    assert response.status_code == 200


# todo: (9) Тест неудачного получения информации о пользователе
@pytest.mark.parametrize("username, password", [
    ("gelo121region", "string1"),
])
async def test_user_me_unauthorized(username, password, ac: AsyncClient):
    headers = {
        "Authorization": "Bearer " + "token"
    }
    response = await ac.get("/api/user/me", headers=headers)
    assert response.status_code == 401


# todo: (10) Тест успешного изменения данных пользователя
@pytest.mark.parametrize("username, password", [
    ("gelo121region", "string1"),
])
async def test_user_update(username, password, ac: AsyncClient):
    user_data = {
        "username": username,
        "password": password
    }
    response = await ac.post("/api/auth/jwt/login", data=user_data)
    assert response.status_code == 200
    assert response.json()['access_token'] is not None

    token = response.json()['access_token']

    headers = {
        "Authorization": "Bearer " + token
    }

    user_patch_data = {
        "email": "user@mail.ru",
        "is_active": True,
        "is_superuser": True,
        "is_verified": True,
        "last_name": "string",
        "first_name": "string",
        "surname": "string"
    }
    response = await ac.patch("/api/user/me", headers=headers, json=user_patch_data)
    assert response.status_code == 200


# todo: (11) Тест неудачного изменения данных пользователя
async def test_user_update_unauthorized(ac: AsyncClient):
    headers = {
        "Authorization": "Bearer " + "token"
    }

    user_patch_data = {
        "password": "string1",
        "email": "user@mail.ru",
        "is_active": True,
        "is_superuser": True,
        "is_verified": True,
        "username": "gelo121region",
        "last_name": "a",
        "first_name": "abs",
        "surname": "sd"
    }
    response = await ac.patch("/api/user/me", headers=headers, json=user_patch_data)
    assert response.status_code == 401


# todo: (27) Получение данных текущего пользователя и обновление его профиля:
@pytest.mark.parametrize("username, password", [
    ("gelo121region", "string1"),
])
async def test_user_get_me_and_update_me(username, password, ac: AsyncClient):
    user_data = {
        "username": username,
        "password": password
    }
    response = await ac.post("/api/auth/jwt/login", data=user_data)
    assert response.status_code == 200
    assert response.json()['access_token'] is not None

    token = response.json()['access_token']

    headers = {
        "Authorization": "Bearer " + token
    }
    #  Get
    response = await ac.get("/api/user/me", headers=headers)
    assert response.status_code == 200

    get_me_obj = response.json()

    # Patch
    user_patch_data = {
        "email": "user@mail.ru",
        "is_active": True,
        "is_superuser": True,
        "is_verified": True,
        "last_name": "New surname",
        "first_name": "New Name",
        "surname": "New surname"
    }
    response = await ac.patch("/api/user/me", headers=headers, json=user_patch_data)
    assert response.status_code == 200

    #  Get
    response = await ac.get("/api/user/me", headers=headers)
    assert response.status_code == 200
    assert response.json() != get_me_obj
