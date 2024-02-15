from typing import List

import pytest

from conftest import async_session_maker
from room.crud import insert_room, delete_room, get_room, filter_rooms
from room.schemas import RoomReadRequest, RoomBaseInfoForUserRequest
from user.crud import get_user_by_username
from user.schemas import UserReadRequest


@pytest.mark.parametrize("username, room_name", [
    ("four123f", "string1"),
])
async def test_insert_room_func(username, room_name):
    async with async_session_maker() as session:
        room: RoomReadRequest = await insert_room(session, username, room_name)

        assert room is not None
        assert room.room_name == room_name
        assert room.members is not None
        assert not room.messages
        assert room.room_active is False


async def test_delete_room_func():
    async with async_session_maker() as session:
        username = 'Gelo123g'
        room_name = 'Sample Room Delete'

        await insert_room(session, username, room_name)
        await delete_room(session, room_name)

        room = await get_room(session, room_name)

        assert room is None


async def test_get_room():
    async with async_session_maker() as session:
        username = 'Gelo123g'
        room_name = 'Sample Room Get'

        await insert_room(session, username, room_name)

        room: RoomReadRequest = await get_room(session, room_name)

        assert room is not None
        assert room.room_name == 'Sample Room Get'


async def test_filter_rooms():
    async with async_session_maker() as session:
        username = 'Gelo123g'
        room_name_template = 'Sample Room Filter'
        created_rooms = []

        for i in range(0, 2):
            room_name = f'Sample Room Filter {i}'
            await insert_room(session, username, room_name)
            created_rooms.append(room_name)

        user: UserReadRequest = await get_user_by_username(session, username)
        result: List[RoomBaseInfoForUserRequest] = await filter_rooms(session, user.user_id, room_name_template)

        for room in result:
            assert room.room_name in created_rooms


async def test_add_user_to_room():
    pass
