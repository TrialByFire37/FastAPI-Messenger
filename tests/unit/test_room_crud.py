from unittest.mock import AsyncMock, MagicMock
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound

from room.crud import insert_room, delete_room, add_user_to_room, set_user_room_activity, \
    alter_favorite, get_user_favorite_like_room_name, set_room_activity


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_request():
    return AsyncMock()


# async def test_get_room():
#     # Создаем мок объекты
#     session = Mock(spec=AsyncSession)
#     room_instance = Mock()
#     room_instance.room_id = 1
#     room_instance.room_name = 'test_room'
#     room_instance.is_active = True
#     room_instance.creation_date = '2024-03-08'
#
#
#     # Настраиваем поведение моков
#     session.execute.return_value = Mock(one=Mock(return_value=room_instance))
#
#     result = await get_room(session, 'test_room')
#
#     # Проверяем, что функция вызывала нужные методы с правильными аргументами
#     session.execute.assert_any_call(select(room).filter_by(room_name='test_room'))
#     session.commit.assert_called_once()
#
#     session.execute.assert_any_call(select(room_user).join(room).filter_by(room_name='test_room'))
#     session.commit.assert_called_once()
#
#     session.execute.assert_any_call(select(message).join(room).filter_by(room_name='test_room'))
#     session.commit.assert_called_once()
#
#     # Проверяем возвращаемый результат
#     assert result.room_id == room_instance.room_id
#     assert result.room_name == room_instance.room_name
#     assert result.room_active == room_instance.is_active
#     assert result.room_creation_date == room_instance.creation_date


# @patch('room.crud.select')
# @patch('room.crud.and_')
# @patch('room.crud.AsyncSession')
# async def test_filter_rooms(mock_session, mock_and, mock_select):
#     # Создаем моки
#     mock_query = AsyncMock()
#     mock_query.fetchall.return_value = [(1, 'room1', True), (2, 'room2', False)]
#     mock_execute = AsyncMock()
#     mock_execute.return_value = mock_query
#     mock_session.execute.return_value = mock_execute
#
#     # Вызываем функцию
#     rooms = await filter_rooms(mock_session, 1, 'room', 1, 10)
#
#     # Проверяем вызовы моков
#     mock_select.assert_called_once()
#     mock_and.assert_called_once()
#     mock_session.execute.assert_called_once()


# todo: все ок

async def test_insert_room(mock_session):
    await insert_room(mock_session, "test_username", "test_room")
    mock_session.execute.assert_called()


async def test_mock_insert_room_integrity_error(mock_session):
    mock_session.execute.side_effect = IntegrityError(None, None, None)
    with pytest.raises(ValueError):
        await insert_room(mock_session, "test_username", "test_room")
    mock_session.rollback.assert_called()


async def test_mock_insert_room_exception(mock_session):
    mock_session.execute.side_effect = Exception
    with pytest.raises(Exception):
        await insert_room(mock_session, "test_username", "test_room")
    mock_session.rollback.assert_called()


async def test_delete_room():
    session = Mock(spec=AsyncSession)
    room_instance = Mock()
    room_instance.room_id = 1
    session.execute.return_value = Mock(one=Mock(return_value=room_instance))
    await delete_room(session, 'test_room')


async def test_mock_delete_room_no_result_found(mock_session):
    mock_session.execute.side_effect = NoResultFound
    with pytest.raises(NoResultFound):
        await delete_room(mock_session, "test_room")


async def test_mock_delete_room_exception(mock_session):
    mock_session.execute.side_effect = Exception
    await delete_room(mock_session, "test_room")
    mock_session.rollback.assert_called()


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

    assert result is True  # Expecting True because entity_room_user is None


async def test_mock_add_user_to_room_existing_user(mock_session):
    mock_session.execute.return_value.scalar_one_or_none.return_value = True
    result = await add_user_to_room(mock_session, "test_username", "test_room")
    mock_session.execute.assert_called()
    assert result is False


async def test_mock_add_user_to_room_no_result_found(mock_session):
    mock_session.execute.side_effect = NoResultFound
    with pytest.raises(NoResultFound):
        await add_user_to_room(mock_session, "test_username", "test_room")


async def test_mock_add_user_to_room_exception(mock_session):
    mock_session.execute.side_effect = Exception
    result = await add_user_to_room(mock_session, "test_username", "test_room")
    mock_session.rollback.assert_called()
    assert result is None


async def test_mock_set_user_room_activity(mock_session):
    await set_user_room_activity(mock_session, "test_username", "test_room", True)
    mock_session.execute.assert_called()


async def test_mock_set_user_room_activity_exception(mock_session):
    mock_session.execute.side_effect = Exception
    await set_user_room_activity(mock_session, "test_username", "test_room", True)
    mock_session.rollback.assert_called()


async def test_mock_set_room_activity(mock_session):
    await set_room_activity(mock_session, "test_room", True)
    mock_session.execute.assert_called()


async def test_mock_set_room_activity_exception(mock_session):
    mock_session.execute.side_effect = Exception
    await set_room_activity(mock_session, "test_room", True)
    mock_session.rollback.assert_called()


async def test_mock_alter_favorite_existing_user(mock_session, mock_request):
    mock_session.execute.return_value.scalar_one_or_none.return_value = True
    await alter_favorite(mock_session, 1, mock_request)
    mock_session.execute.assert_called()
    mock_session.commit.assert_called()


async def test_mock_alter_favorite_new_user( mock_request):
    session = AsyncMock()
    session.execute = AsyncMock()

    session.execute.side_effect = [
        MagicMock(scalar_one=MagicMock()),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        MagicMock(scalar_one=MagicMock()),
    ]
    await alter_favorite(session, 1, mock_request)
    session.commit.assert_called()


async def test_mock_alter_favorite_no_result_found(mock_session, mock_request):
    mock_session.execute.side_effect = NoResultFound
    await alter_favorite(mock_session, 1, mock_request)
    mock_session.rollback.assert_called()


async def test_mock_alter_favorite_exception(mock_session, mock_request):
    mock_session.execute.side_effect = Exception
    await alter_favorite(mock_session, 1, mock_request)
    mock_session.rollback.assert_called()


async def test_mock_get_user_favorite_like_room_name_nonexistent_user(mock_session):
    mock_session.execute.side_effect = NoResultFound
    with pytest.raises(NoResultFound):
        await get_user_favorite_like_room_name(mock_session, "Sample Room", 1)
