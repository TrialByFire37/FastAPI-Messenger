from typing import List

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import NoResultFound, IntegrityError

from auth.schemas import UserRead
from tests.conftest import async_session_maker
from user.crud import get_user_by_id, get_user_by_username, update_user_data, get_users_in_room
from user.schemas import UserReadRequest, UserUpdateRequest


async def test_update_user_image(ac: AsyncClient):
    login_data = {
        "username": "gelo21region",
        "password": "string1"
    }
    login_response = await ac.post("/api/auth/jwt/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "token_type" in login_response.json()

    token = login_response.json()['access_token']

    headers = {
        "Authorization": "Bearer " + token
    }
    get_me_response = await ac.get("/api/user/me", headers=headers)
    assert get_me_response.status_code == 200, "Failed to get me"

    get_me_response_json = get_me_response.json()

    current_user: UserRead = UserRead(
        id=get_me_response_json['id'],
        email=get_me_response_json['email'],
        username=get_me_response_json['username'],
        last_name=get_me_response_json['last_name'],
        first_name=get_me_response_json['first_name'],
        surname=get_me_response_json['surname'],
        image_url=get_me_response_json['image_url'],
        creation_date=get_me_response_json['creation_date'],
        is_active=get_me_response_json['is_active'],
        is_superuser=get_me_response_json['is_superuser'],
        is_verified=get_me_response_json['is_verified']
    )

    # Сначала проверим, что у пользователя нет изображения
    assert current_user.image_url is None

    # Теперь сделаем запрос для обновления изображения
    with open("resources/1653975016_28.jpg", "rb") as image_file:
        files = {"file": ("test_image.jpg", image_file, "image/jpg")}
        response = await ac.post("/api/user/profile_picture", files=files, headers=headers)

    assert response.status_code == 200, "Failed to update user image"

    # Проверим, что изображение успешно обновлено
    get_me_response = await ac.get("/api/user/me", headers=headers)
    assert get_me_response.status_code == 200, "Failed to get me"
    get_me_response_json = get_me_response.json()
    assert "image_url" in get_me_response_json
    assert get_me_response_json["image_url"] is not None
