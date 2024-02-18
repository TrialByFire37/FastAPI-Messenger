from typing import List

import pytest
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError, DataError, NoResultFound, DBAPIError

from conftest import async_session_maker
from models.models import room_user, user, room
from room.crud import insert_room, delete_room, get_room, filter_rooms, add_user_to_room, set_room_activity, \
    set_user_room_activity, get_rooms, get_user_favorite, alter_favorite, get_user_favorite_like_room_name
from room.schemas import RoomReadRequest, RoomBaseInfoForUserRequest, FavoriteRequest
from user.crud import get_user_by_username
from user.schemas import UserReadRequest


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Insert"),
])
async def test_insert_room(username, room_name):
    async with async_session_maker() as session:
        inserted_room: RoomReadRequest = await insert_room(session, username, room_name)

        assert inserted_room is not None
        assert inserted_room.room_name == room_name
        assert inserted_room.members is not None
        assert not inserted_room.messages
        assert inserted_room.room_active is False


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Insert"),
])
async def test_insert_existing_room(username, room_name):
    async with async_session_maker() as session:
        with pytest.raises(ValueError):
            await insert_room(session, username, room_name)


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Insert ROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOM"),
])
async def test_insert_incorrect_name_room(username, room_name):
    async with async_session_maker() as session:
        with pytest.raises(DBAPIError):
            await insert_room(session, username, room_name)


@pytest.mark.parametrize("username, room_name", [
    ("RaNdOm_NoNaMe1337", "Sample Room Insert Non-Existing User"),
])
async def test_insert_room_non_existing_user(username, room_name):
    async with async_session_maker() as session:
        with pytest.raises(NoResultFound):
            await insert_room(session, username, room_name)


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Delete"),
])
async def test_delete_room(username, room_name):
    async with async_session_maker() as session:
        await insert_room(session, username, room_name)
        await delete_room(session, room_name)

        current_room = await get_room(session, room_name)

        assert current_room is None


# todo: проверить, всё ли здесь ок с обработкой NoResultFound в crud (там добавили ещё обработку этого
# исключения отдельно, а нужен именно оно здесь по логике
@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Delete Non-Existing"),
])
async def test_delete_non_existing_room(username, room_name):
    async with async_session_maker() as session:
        with pytest.raises(NoResultFound):
            await delete_room(session, room_name)


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Get"),
])
async def test_get_room(username, room_name):
    async with async_session_maker() as session:
        await insert_room(session, username, room_name)

        current_room: RoomReadRequest = await get_room(session, room_name)

        assert current_room is not None
        assert current_room.room_name == 'Sample Room Get'


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Get Non-Existing"),
])
async def test_get_non_existing_room(username, room_name):
    async with async_session_maker() as session:
        current_room = await get_room(session, room_name)

        assert current_room is None


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

        current_user: UserReadRequest = await get_user_by_username(session, username)
        result: List[RoomBaseInfoForUserRequest] = await filter_rooms(session, current_user.user_id, room_name_template)

        for created_room in result:
            assert created_room.room_name in created_rooms


@pytest.mark.parametrize("username, room_name_template", [
    ("gelo123g", "Sample Room Filter Non-Existing"),
])
async def test_filter_non_existing_rooms(username, room_name_template):
    async with async_session_maker() as session:
        current_user = await get_user_by_username(session, username)
        result = await filter_rooms(session, current_user.user_id, room_name_template)

        assert len(result) == 0


@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Add User Here"),
])
async def test_add_user_to_room(username, room_name):
    async with async_session_maker() as session:
        current_room = await insert_room(session, username, room_name)
        await add_user_to_room(session, username, current_room.room_name)

        assert any(current_user.username == username for current_user in current_room.members)


# todo: проверить, всё ли здесь ок с обработкой NoResultFound в crud (там добавили ещё обработку этого
# исключения отдельно, а нужен именно оно здесь по логике
@pytest.mark.parametrize("username, room_name", [
    ("gelo123g", "Sample Room Add User Nowhere"),
])
async def test_add_user_to_non_existing_room(username, room_name):
    async with async_session_maker() as session:
        with pytest.raises(NoResultFound):
            await add_user_to_room(session, username, room_name)


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
        await insert_room(session, username, room_name)
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

        for current_room in rooms:
            assert isinstance(current_room, RoomBaseInfoForUserRequest)


@pytest.mark.parametrize("username", [
    "GaNeNkO_GlEb",
])
async def test_get_rooms_non_existing_user(username):
    async with async_session_maker() as session:
        with pytest.raises(NoResultFound):
            current_user = await get_user_by_username(session, username)
            current_user_id = current_user.user_id

            await get_rooms(session, current_user_id)


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


@pytest.mark.parametrize("username", [
    "GaNeNkO_GlEb",
])
async def test_get_user_favorite_nonexistent_user(username):
    async with async_session_maker() as session:
        with pytest.raises(NoResultFound):
            current_user = await get_user_by_username(session, username)
            current_user_id = current_user.user_id

            await get_user_favorite(session, current_user_id)


@pytest.mark.parametrize("username", [
    "no_favorites_dude1",
])
async def test_get_user_empty_favorite(username):
    async with async_session_maker() as session:
        current_user = await get_user_by_username(session, username)
        current_user_id = current_user.user_id
        favorites = await get_user_favorite(session, current_user_id)

        assert len(favorites) == 0


@pytest.mark.parametrize("username, room_name_template, is_chosen", [
    ("gelo123g", "Sample Room Get User Favorite Like", True),
])
async def test_get_user_favorite_like_room_name(username, room_name_template, is_chosen):
    async with async_session_maker() as session:
        current_user = await get_user_by_username(session, username)
        current_user_id = current_user.user_id

        created_rooms = []
        for i in range(0, 2):
            room_name = ' '.join([room_name_template, str(i)])
            await insert_room(session, username, room_name)
            created_rooms.append(room_name)
            favrequest = FavoriteRequest(room_name=room_name, is_chosen=is_chosen)
            await alter_favorite(session, current_user_id, favrequest)

        favorites = await get_user_favorite_like_room_name(session, room_name, current_user_id)

        for fav_room in favorites:
            assert fav_room.room_name in created_rooms


@pytest.mark.parametrize("username, room_name_template", [
    ("gelo123g", "Sample Room Fav Non-Existing Template"),
])
async def test_get_user_favorite_like_room_name_nonexistent_template(username, room_name_template):
    async with async_session_maker() as session:
        current_user = await get_user_by_username(session, username)
        current_user_id = current_user.user_id
        favorites = await get_user_favorite_like_room_name(session, room_name_template, current_user_id)

        assert len(favorites) == 0


@pytest.mark.parametrize("username, room_name_template", [
    ("GaNeNkO_GlEb", "Sample Room"),
])
async def test_get_user_favorite_like_room_name_nonexistent_user(username, room_name_template):
    async with async_session_maker() as session:
        with pytest.raises(NoResultFound):
            current_user = await get_user_by_username(session, username)
            current_user_id = current_user.user_id

            await get_user_favorite_like_room_name(session, room_name_template, current_user_id)


@pytest.mark.parametrize("username, room_name, is_chosen", [
    ("gelo123g", "Sample Room Alter Favorite", True),
])
async def test_alter_favorite(username, room_name, is_chosen):
    async with async_session_maker() as session:
        current_user = await get_user_by_username(session, username)
        current_user_id = current_user.user_id

        await insert_room(session, username, room_name)

        favorite_request = FavoriteRequest(room_name=room_name, is_chosen=is_chosen)
        await alter_favorite(session, current_user_id, favorite_request)

        # Получаем список избранных комнат пользователя
        favorites = await get_user_favorite(session, current_user_id)

        # Проверяем, что статус избранного для комнаты был изменен правильно
        assert any(favorite.room_name == room_name and favorite.is_favorites == is_chosen for favorite in favorites)


# todo: NoResultFound в crud (в отличие от других функций, здесь я ничего не менял в круде - там уже написана
# другая обработка, хз как тут быть
@pytest.mark.parametrize("username, room_name, is_chosen", [
    ("gelo123g", "Alter Favorite Nonexistent Room", True),
])
async def test_alter_favorite_nonexistent_room(username, room_name, is_chosen):
    async with async_session_maker() as session:
        current_user = await get_user_by_username(session, username)
        current_user_id = current_user.user_id

        favorite_request = FavoriteRequest(room_name=room_name, is_chosen=is_chosen)
        with pytest.raises(NoResultFound):
            await alter_favorite(session, current_user_id, favorite_request)


@pytest.mark.parametrize("username, room_name, is_chosen", [
    ("GaNeNkO_GlEb", "Sample Room", True),
])
async def test_alter_favorite_nonexistent_user(username, room_name, is_chosen):
    async with async_session_maker() as session:
        with pytest.raises(NoResultFound):
            current_user = await get_user_by_username(session, username)
            current_user_id = current_user.user_id

            favorite_request = FavoriteRequest(room_name=room_name, is_chosen=is_chosen)
            await alter_favorite(session, current_user_id, favorite_request)
