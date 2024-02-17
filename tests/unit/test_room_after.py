from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from conftest import async_session_maker
from message.crud import (upload_message_to_room, get_messages_in_room, upload_message_with_file_to_room,
                          get_members_in_room)


@pytest.mark.parametrize("username, room_name, message", [
    ("four123f", "string1", "Hello, World!"),
])
async def test_upload_message_to_room(username, room_name, message):
    async with async_session_maker() as session:
        value = await upload_message_to_room(session, room_name, username, message)
        assert value is True


@pytest.mark.parametrize("username, room_name, message", [
    ("four123f1", "string1", "Hello, World!"),
])
async def test_upload_message_to_room_fail_user_name(username, room_name, message):
    async with async_session_maker() as session:
        value = await upload_message_to_room(session, room_name, username, message)
        assert value is False


@pytest.mark.parametrize("username, room_name, message", [
    ("four123f", "string12", "Hello, World!"),
])
async def test_upload_message_to_room_fail_room(username, room_name, message):
    async with async_session_maker() as session:
        value = await upload_message_to_room(session, room_name, username, message)
        assert value is False


@pytest.mark.parametrize("username, room_name, message", [
    ("four123f1", "string12", "Hello, World!"),
])
async def test_upload_message_to_room_fail_user_name_and_room_name(username, room_name, message):
    async with async_session_maker() as session:
        value = await upload_message_to_room(session, room_name, username, message)
        assert value is False


@pytest.mark.parametrize("room_id", [
    3,
])
async def test_get_messages_in_room_room_is_not_empty(room_id):
    async with async_session_maker() as session:
        value = await get_messages_in_room(session, room_id)
        assert value is not None
        assert value[0].message is not None
        assert value[0].message == "Hello, World!"
        assert value[0].media_file_url is None
        assert value[0].user is not None


@pytest.mark.parametrize("room_id", [
    1,
])
async def test_get_messages_in_room_room_is_empty(room_id):
    async with async_session_maker() as session:
        value = await get_messages_in_room(session, room_id)
        assert value is not None
        assert len(value) == 0


@pytest.mark.parametrize("room_id", [
    1,
])
async def test_get_members_in_room_room_is_empty(room_id):
    async with async_session_maker() as session:
        value = await get_members_in_room(session, room_id)
        assert value is not None
        assert len(value) > 0
        assert value[0].user_id is not None
        assert value[0].user_id == 1
        assert value[0].username is not None
        assert value[0].username == "gelo21region"


@pytest.mark.parametrize("room_id", [
    1,
])
async def test_get_members_in_room_room_is_empty(room_id):
    async with async_session_maker() as session:
        value = await get_members_in_room(session, room_id)
        assert value is not None
        assert len(value) > 0
        assert value[0].user_id is not None
        assert value[0].user_id == 1
        assert value[0].username is not None
        assert value[0].username == "gelo21region"
        assert value[0].profile_pic_img_src is None
