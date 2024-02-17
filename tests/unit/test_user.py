from typing import List

import pytest
from sqlalchemy.exc import NoResultFound

from conftest import async_session_maker
from user.crud import get_user_by_id, get_user_by_username, get_users_in_room
from user.schemas import UserReadRequest


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


async def test_get_users_in_room():
    async with async_session_maker() as session:
        users_read_request: List[UserReadRequest] = await get_users_in_room(session, 1)
        assert users_read_request is not None
        assert users_read_request[0].user_id == 1
        assert users_read_request[0].username == "gelo21region"
        assert users_read_request[0].email == "popov.gleb.01@mail.ru"
        assert users_read_request[0].image_url is None
