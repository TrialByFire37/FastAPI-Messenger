import pytest
from httpx import AsyncClient

from auth.schemas import UserRead


# todo: (12) Тест успешного добавления изображения профиля
# @pytest.mark.parametrize("username, password", [
#     ("gelo121region", "string1"),
# ])
# async def test_update_user_image(username, password, ac: AsyncClient):
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
#     headers = {
#         "Authorization": "Bearer " + token
#     }
#     get_me_response = await ac.get("/api/user/me", headers=headers)
#     assert get_me_response.status_code == 200, "Failed to get me"
#
#     get_me_response_json = get_me_response.json()
#
#     current_user: UserRead = UserRead(
#         id=get_me_response_json['id'],
#         email=get_me_response_json['email'],
#         username=get_me_response_json['username'],
#         last_name=get_me_response_json['last_name'],
#         first_name=get_me_response_json['first_name'],
#         surname=get_me_response_json['surname'],
#         image_url=get_me_response_json['image_url'],
#         creation_date=get_me_response_json['creation_date'],
#         is_active=get_me_response_json['is_active'],
#         is_superuser=get_me_response_json['is_superuser'],
#         is_verified=get_me_response_json['is_verified']
#     )
#
#     # Сначала проверим, что у пользователя нет изображения
#     assert current_user.image_url is None
#
#     # Теперь сделаем запрос для обновления изображения
#     with open("tests/resources/test.jpeg", "rb") as image_file:
#         files = {"file": ("test_image.jpg", image_file, "image/jpg")}
#         response = await ac.post("/api/user/profile_picture", files=files, headers=headers)
#
#     assert response.status_code == 200, "Failed to update user image"
#
#     # Проверим, что изображение успешно обновлено
#     get_me_response = await ac.get("/api/user/me", headers=headers)
#     assert get_me_response.status_code == 200, "Failed to get me"
#     get_me_response_json = get_me_response.json()
#     assert "image_url" in get_me_response_json
#     assert get_me_response_json["image_url"] is not None


# todo: (13) Тест неудачного добавления изображения профиля
async def test_update_user_image_unauthorized(ac: AsyncClient):
    headers = {
        "Authorization": "Bearer " + "token"
    }

    with open("tests/resources/test.jpeg", "rb") as image_file:
        files = {"file": ("test_image.jpg", image_file, "image/jpg")}
        response = await ac.post("/api/user/profile_picture", files=files, headers=headers)

    assert response.status_code == 401

