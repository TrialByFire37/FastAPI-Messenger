from typing import List

import pytest
from sqlalchemy import select, and_

from auth.schemas import UserRead
from conftest import async_session_maker
from models.models import room_user, user, room
from room.crud import insert_room, delete_room, get_room, filter_rooms, add_user_to_room, set_room_activity, \
    set_user_room_activity, get_rooms, get_user_favorite, alter_favorite, get_user_favorite_like_room_name
from room.schemas import RoomReadRequest, RoomBaseInfoForUserRequest, RoomBaseInfoForAllUserRequest, FavoriteRequest
from user.crud import get_user_by_username
from user.schemas import UserReadRequest


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Insert"),
])
async def test_insert_room_func(username, room_name):
    async with async_session_maker() as session:
        room: RoomReadRequest = await insert_room(session, username, room_name)

        assert room is not None
        assert room.room_name == room_name
        assert room.members is not None
        assert not room.messages
        assert room.room_active is False


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Delete"),
])
async def test_delete_room_func(username, room_name):
    async with async_session_maker() as session:
        await insert_room(session, username, room_name)
        await delete_room(session, room_name)

        room = await get_room(session, room_name)

        assert room is None


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Get"),
])
async def test_get_room(username, room_name):
    async with async_session_maker() as session:
        await insert_room(session, username, room_name)

        room: RoomReadRequest = await get_room(session, room_name)

        assert room is not None
        assert room.room_name == 'Sample Room Get'


@pytest.mark.parametrize("username, room_name_template", [
    ("gelo123g", "Sample Room Filter"),
])
async def test_filter_rooms(username, room_name_template):
    async with async_session_maker() as session:
        created_rooms = []

        for i in range(0, 2):
            room_name = ' '.join([room_name_template, str(i)])
            await insert_room(session, username, room_name)
            created_rooms.append(room_name)

        user: UserReadRequest = await get_user_by_username(session, username)
        result: List[RoomBaseInfoForUserRequest] = await filter_rooms(session, user.user_id, room_name_template)

        for room in result:
            assert room.room_name in created_rooms


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Add User Here"),
])
async def test_add_user_to_room(username, room_name):
    async with async_session_maker() as session:
        room = await insert_room(session, username, room_name)
        await add_user_to_room(session, username, room.room_name)

        assert any(user.username == username for user in room.members)


@pytest.mark.parametrize("username, room_name, is_active", [
    ("gelo123g", "Sample Room Set User-Room Activity", True),
])
async def test_set_user_room_activity(username, room_name, is_active):
    async with async_session_maker() as session:
        await insert_room(session, username, room_name)
        await add_user_to_room(session, username, room_name)

        await set_user_room_activity(session, username, room_name, is_active)

        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
        user_instance = (await session.execute(select(user).filter_by(username=username))).scalar_one()
        room_user_instance = (await session.execute(
            select(room_user.c.is_active).where(
                and_(room_user.c.user == user_instance, room_user.c.room == room_instance)
            )
        )).scalar_one()

        assert room_user_instance


@pytest.mark.parametrize("username, room_name, activity_bool", [
    ("gelo123g", "Sample Room Set Room Activity", True),
])
async def test_set_room_activity(username, room_name, activity_bool):
    async with async_session_maker() as session:
        inserted_room = await insert_room(session, username, room_name)
        await set_room_activity(session, room_name, activity_bool)
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).one()

        assert room_instance.is_active == activity_bool


@pytest.mark.parametrize("username", [
    "gelo123g",
])
async def test_get_rooms(username):
    async with async_session_maker() as session:
        current_user = await get_user_by_username(session, username)
        current_user_id = current_user.user_id

        rooms = await get_rooms(session, current_user_id)

        for room in rooms:
            assert isinstance(room, RoomBaseInfoForUserRequest)


@pytest.mark.parametrize("username, room_name, is_chosen", [
    ("gelo123g", "Sample Room Get User Favorite", True)
])
async def test_get_user_favorite(username, room_name, is_chosen):
    async with async_session_maker() as session:
        await insert_room(session, username, room_name)

        current_user = await get_user_by_username(session, username)
        current_user_id = current_user.user_id

        favrequest = FavoriteRequest(room_name=room_name, is_chosen=is_chosen)
        await alter_favorite(session, current_user_id, favrequest)
        favorites = await get_user_favorite(session, current_user_id)

        assert any(favorite.room_name == room_name for favorite in favorites)


@pytest.mark.parametrize("username, room_name_template, is_chosen", [
    ("gelo123g", "Sample Room Get User Favorite Like", True),
])
async def test_get_user_favorite_like_room_name(username, room_name_template, is_chosen):
    async with async_session_maker() as session:
        user = await get_user_by_username(session, username)
        current_user_id = user.user_id

        created_rooms = []
        for i in range(0, 2):
            room_name = ' '.join([room_name_template, str(i)])
            await insert_room(session, username, room_name)
            created_rooms.append(room_name)
            favrequest = FavoriteRequest(room_name=room_name, is_chosen=is_chosen)
            await alter_favorite(session, current_user_id, favrequest)

        favorites = await get_user_favorite_like_room_name(session, room_name, current_user_id)

        for room in favorites:
            assert room.room_name in created_rooms


@pytest.mark.parametrize("username, room_name, is_chosen", [
    ("gelo123g", "Sample Room Alter Favorite", True),
])
async def test_alter_favorite(username, room_name, is_chosen):
    async with async_session_maker() as session:
        user = await get_user_by_username(session, username)
        current_user_id = user.user_id

        await insert_room(session, username, room_name)

        favorite_request = FavoriteRequest(room_name=room_name, is_chosen=is_chosen)
        await alter_favorite(session, current_user_id, favorite_request)

        # Получаем список избранных комнат пользователя
        favorites = await get_user_favorite(session, current_user_id)

        # Проверяем, что статус избранного для комнаты был изменен правильно
        assert any(favorite.room_name == room_name and favorite.is_favorites == is_chosen for favorite in favorites)