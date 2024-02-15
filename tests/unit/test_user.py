from typing import List

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import NoResultFound

from auth.schemas import UserRead
from tests.conftest import async_session_maker
from user.crud import get_user_by_id, get_user_by_username, update_user_data, get_users_in_room
from user.schemas import UserReadRequest, UserUpdateRequest


async def test_get_user_by_id():
    async with async_session_maker() as session:
        current_user: UserReadRequest = await get_user_by_id(session, 1)
        assert current_user is not None
        assert current_user.user_id == 1
        assert current_user.username == "gelo21region"
        assert current_user.email == "popov.gleb.01@mail.ru"
        assert current_user.image_url is None


async def test_get_user_by_id_fail():
    async with async_session_maker() as session:
        with pytest.raises(NoResultFound):
            await get_user_by_id(session, 1_000_000)


async def test_get_user_by_username():
    async with async_session_maker() as session:
        current_user: UserReadRequest = await get_user_by_username(session, "gelo21region")
        assert current_user is not None
        assert current_user.user_id == 1
        assert current_user.username == "gelo21region"
        assert current_user.email == "popov.gleb.01@mail.ru"
        assert current_user.image_url is None


async def test_get_user_by_username_fail():
    async with async_session_maker() as session:
        with pytest.raises(NoResultFound):
            await get_user_by_username(session, "Gelo123g1")


async def test_update_user_data(ac: AsyncClient):
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
    request: UserUpdateRequest = UserUpdateRequest(
        password="string1",
        username="gelo21region",
        last_name="popov",
        first_name="gleb",
    )
    async with async_session_maker() as session:
        await update_user_data(session, current_user, request)
        current_user: UserReadRequest = await get_user_by_username(session, "gelo21region")
        assert current_user is not None
        assert current_user.user_id == 1
        assert current_user.username == "gelo21region"
        assert current_user.email == "popov.gleb.01@mail.ru"


async def test_update_user_data_fail(ac: AsyncClient):
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
    request: UserUpdateRequest = UserUpdateRequest(
        password="string1",
        username="four123f",
        last_name="popov",
        first_name="gleb",
    )
    async with async_session_maker() as session:
        result = await update_user_data(session, current_user, request)
        assert not result, "Expected update_user_data to fail, but it succeeded"


async def test_get_users_in_room():
    async with async_session_maker() as session:
        users_read_request: List[UserReadRequest] = await get_users_in_room(session, 1)
        assert users_read_request is not None
        assert users_read_request[0].user_id == 1
        assert users_read_request[0].username == "gelo21region"
        assert users_read_request[0].email == "popov.gleb.01@mail.ru"
        assert users_read_request[0].image_url is None
