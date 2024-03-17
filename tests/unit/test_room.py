from unittest.mock import AsyncMock, MagicMock
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound

from room.crud import insert_room, delete_room, add_user_to_room, set_user_room_activity, \
    alter_favorite, get_user_favorite_like_room_name, set_room_activity, filter_rooms


@pytest.fixture
def mock_request():
    return AsyncMock()


# todo: (32) Тест геттера комнаты (Failed)
# async def test_get_room(mock_db_session):
#     mock_db_session.execute.return_value.one.return_value = AsyncMock(
#         room_id=123, room_name='test_room', is_active=True, creation_date='2024-03-13'
#     )
#     mock_db_session.commit.return_value = None
#     mock_db_session.execute.return_value.one.side_effect = [
#         AsyncMock(room_id=123, room_name='test_room', is_active=True, creation_date='2024-03-13'),
#         None
#     ]
#     mock_get_users_in_room = AsyncMock(return_value=['user1', 'user2'])
#     mock_get_messages_in_room = AsyncMock(return_value=['message1', 'message2'])
#
#     with patch('room.crud.get_users_in_room', mock_get_users_in_room), \
#          patch('room.crud.get_messages_in_room', mock_get_messages_in_room):
#
#         room = await get_room(mock_db_session, 'test_room')
#
#         assert isinstance(room, RoomReadRequest)
#         assert room.room_id == 123
#         assert room.room_name == 'test_room'
#         assert room.members == ['user1', 'user2']
#         assert room.messages == ['message1', 'message2']
#         assert room.room_active
#         assert room.room_creation_date == '2024-03-13'
#
#         room = await get_room(mock_db_session, 'non_existing_room')
#         assert room is None
#
#         mock_db_session.execute.assert_called()
#         mock_db_session.commit.assert_called()
#         mock_get_users_in_room.assert_called()
#         mock_get_messages_in_room.assert_called()


# todo: (33) Тест фильтрации комнаты по имени
async def test_filter_rooms(mock_db_session):
    mock_query = AsyncMock()
    mock_query.fetchall.return_value = [(1, 'room1', True, '2024-03-08'), (2, 'room2', True, '2024-03-08')]
    mock_execute = AsyncMock(return_value=mock_query)
    mock_db_session.execute = mock_execute

    rooms = await filter_rooms(mock_db_session, 1, 'room', 1, 10)

    mock_db_session.execute.assert_called()


# todo: (34) Тест добавления комнаты
async def test_insert_room(mock_db_session):
    await insert_room(mock_db_session, "test_username", "test_room")
    mock_db_session.execute.assert_called()


# todo: (35) Тест добавления комнаты - IntegrityError
async def test_mock_insert_room_integrity_error(mock_db_session):
    mock_db_session.execute.side_effect = IntegrityError(None, None, None)
    with pytest.raises(ValueError):
        await insert_room(mock_db_session, "test_username", "test_room")
    mock_db_session.rollback.assert_called()


# todo: (36) Тест добавления комнаты - Exception
async def test_mock_insert_room_exception(mock_db_session):
    mock_db_session.execute.side_effect = Exception
    with pytest.raises(Exception):
        await insert_room(mock_db_session, "test_username", "test_room")
    mock_db_session.rollback.assert_called()


# todo: (37) Тест удаления комнаты
async def test_delete_room():
    session = Mock(spec=AsyncSession)
    room_instance = Mock()
    room_instance.room_id = 1
    session.execute.return_value = Mock(one=Mock(return_value=room_instance))
    await delete_room(session, 'test_room')


# todo: (38) Тест удаления комнаты - NoResultFound
async def test_mock_delete_room_no_result_found(mock_db_session):
    mock_db_session.execute.side_effect = NoResultFound
    with pytest.raises(NoResultFound):
        await delete_room(mock_db_session, "test_room")


# todo: (39) Тест удаления комнаты - Exception
async def test_mock_delete_room_exception(mock_db_session):
    mock_db_session.execute.side_effect = Exception
    await delete_room(mock_db_session, "test_room")
    mock_db_session.rollback.assert_called()


# todo: (40) Тест добавления пользователя в комнату
async def test_add_user_to_room_none_entity_room_user():
    session = AsyncMock()
    session.execute = AsyncMock()

    session.execute.side_effect = [
        MagicMock(scalar_one=MagicMock()),
        MagicMock(scalar_one=MagicMock()),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        MagicMock(scalar_one=MagicMock()),
    ]

    result = await add_user_to_room(session, "test_user", "test_room")

    assert result is True


# todo: (41) Тест добавления пользователя в комнату - пользователь уже есть в ней
async def test_mock_add_user_to_room_existing_user(mock_db_session):
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = True
    result = await add_user_to_room(mock_db_session, "test_username", "test_room")
    mock_db_session.execute.assert_called()
    assert result is False


# todo: (42) Тест добавления пользователя в комнату - NoResultFound
async def test_mock_add_user_to_room_no_result_found(mock_db_session):
    mock_db_session.execute.side_effect = NoResultFound
    with pytest.raises(NoResultFound):
        await add_user_to_room(mock_db_session, "test_username", "test_room")


# todo: (43) Тест добавления пользователя в комнату - Exception
async def test_mock_add_user_to_room_exception(mock_db_session):
    mock_db_session.execute.side_effect = Exception
    result = await add_user_to_room(mock_db_session, "test_username", "test_room")
    mock_db_session.rollback.assert_called()
    assert result is None


# todo: (44) Тест сеттера статуса пользователя в комнате
async def test_mock_set_user_room_activity(mock_db_session):
    await set_user_room_activity(mock_db_session, "test_username", "test_room", True)
    mock_db_session.execute.assert_called()


# todo: (45) Тест сеттера статуса пользователя в комнате - Exception
async def test_mock_set_user_room_activity_exception(mock_db_session):
    mock_db_session.execute.side_effect = Exception
    await set_user_room_activity(mock_db_session, "test_username", "test_room", True)
    mock_db_session.rollback.assert_called()


# todo: (46) Тест сеттера статуса комнаты
async def test_mock_set_room_activity(mock_db_session):
    await set_room_activity(mock_db_session, "test_room", True)
    mock_db_session.execute.assert_called()


# todo: (47) Тест сеттера статуса комнаты - Exception
async def test_mock_set_room_activity_exception(mock_db_session):
    mock_db_session.execute.side_effect = Exception
    await set_room_activity(mock_db_session, "test_room", True)
    mock_db_session.rollback.assert_called()


# todo: (48) Тест работы функции закладки - существующий пользователь
async def test_mock_alter_favorite_existing_user(mock_db_session, mock_request):
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = True
    await alter_favorite(mock_db_session, 1, mock_request)
    mock_db_session.execute.assert_called()
    mock_db_session.commit.assert_called()


# todo: (49) Тест работы функции закладки - новый пользователь
async def test_mock_alter_favorite_new_user(mock_request):
    session = AsyncMock()
    session.execute = AsyncMock()

    session.execute.side_effect = [
        MagicMock(scalar_one=MagicMock()),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        MagicMock(scalar_one=MagicMock()),
    ]
    await alter_favorite(session, 1, mock_request)
    session.commit.assert_called()


# todo: (50) Тест работы функции закладки - NoResultFound
async def test_mock_alter_favorite_no_result_found(mock_db_session, mock_request):
    mock_db_session.execute.side_effect = NoResultFound
    await alter_favorite(mock_db_session, 1, mock_request)
    mock_db_session.rollback.assert_called()


# todo: (51) Тест работы функции закладки - Exception
async def test_mock_alter_favorite_exception(mock_db_session, mock_request):
    mock_db_session.execute.side_effect = Exception
    await alter_favorite(mock_db_session, 1, mock_request)
    mock_db_session.rollback.assert_called()


# todo: (52) Тест работы поиска закладок - нет пользователя
async def test_mock_get_user_favorite_like_room_name_nonexistent_user(mock_db_session):
    mock_db_session.execute.side_effect = NoResultFound
    result = await get_user_favorite_like_room_name(mock_db_session, "Sample Room", 1)
    assert result is None
