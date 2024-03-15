import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from auth.models import User
from message.crud import (upload_message_to_room, get_messages_in_room, upload_message_with_file_to_room,
                          get_members_in_room)
from message.schemas import MemberRead, MessageRead
from models.models import room, user, message
from user.schemas import UserReadRequest


async def test_upload_message_to_room(mock_db_session):
    # Создаем моки для room_id и user_id
    mock_scalar_one = MagicMock()
    mock_scalar_one.return_value = asyncio.Future()
    mock_scalar_one.return_value.set_result(1)

    # Создаем моки для room_name, user_name и message_data
    room_name = "test_room"
    user_name = "test_user"
    message_data = "test_message"

    with patch.object(mock_db_session, "execute", return_value=mock_scalar_one):
        result = await upload_message_to_room(mock_db_session, room_name, user_name, message_data)

    # Проверяем, что был выполнен commit
    mock_db_session.commit.assert_called_once()

    # Проверяем, что результат соответствует ожидаемому
    assert result == True


async def test_upload_message_to_room_fail_user_name(mock_db_session):
    # Создаем моки для room_name, user_name и message_data
    room_name = "test_room"
    user_name = "non_existent_user"  # Пользователь не существует
    message_data = "test_message"

    with patch.object(mock_db_session, "execute", return_value=None):
        result = await upload_message_to_room(mock_db_session, user_name, room_name, message_data)

    # Проверяем, что результат соответствует ожидаемому
    assert result == False


async def test_upload_message_to_room_fail_room(mock_db_session):
    # Создаем моки для room_name, user_name и message_data
    room_name = "non_existent_room"  # Комната не существует
    user_name = "test_user"
    message_data = "test_message"

    with patch.object(mock_db_session, "execute", return_value=None):
        result = await upload_message_to_room(mock_db_session, user_name, room_name, message_data)

    # Проверяем, что результат соответствует ожидаемому
    assert result == False


async def test_upload_message_to_room_fail_user_name_and_room_name(mock_db_session):
    # Создаем моки для room_name, user_name и message_data
    room_name = "non_existent_room"  # Комната не существует
    user_name = "non_existent_user"  # Пользователь не существует
    message_data = "test_message"

    with patch.object(mock_db_session, "execute", return_value=None):
        result = await upload_message_to_room(mock_db_session, user_name, room_name, message_data)

    # Проверяем, что результат соответствует ожидаемому
    assert result == False


# async def test_get_messages_in_room(mock_db_session):
#     # Мокаем результат запроса к базе данных
#     mock_db_session.execute.return_value.fetchall.return_value = [
#         (1, "Hello!", "http://test1.com/test1.jpg", datetime.utcnow(), 1, 1),
#         (2, "How are you?", "http://test2.com/test2.jpg", datetime.utcnow(), 2, 1)
#     ]
#
#     # Мокаем функцию get_user_by_id
#     with patch('user.crud.get_user_by_id', new_callable=AsyncMock) as mock_get_user_by_id:
#         def side_effect(user_id):
#             return UserReadRequest(user_id=user_id, username=f"test{user_id}", email=f"test{user_id}@mail.com", profile_pic_img_src=f"http://test{user_id}.com/test{user_id}.jpg")
#         mock_get_user_by_id.side_effect = side_effect
#
#         # Мокаем session.execute
#         result_proxy_mock = MagicMock()
#         result_proxy_mock.fetchall.return_value = [
#             (1, "Hello!", "http://test1.com/test1.jpg", datetime.utcnow(), 1, 1),
#             (2, "How are you?", "http://test2.com/test2.jpg", datetime.utcnow(), 2, 1)
#         ]
#         mock_db_session.execute.return_value = AsyncMock(return_value=result_proxy_mock)
#
#         # Вызываем функцию, которую тестируем
#         messages = await get_messages_in_room(mock_db_session, 1)
#
#         # Проверяем, что она вернула ожидаемый результат
#         assert len(messages) == 2
#         assert isinstance(messages[0], MessageRead)
#         assert messages[0].message == "Hello!"
#         assert messages[0].media_file_url == "http://test1.com/test1.jpg"
#         assert messages[0].email == "test1@mail.com"
#         assert isinstance(messages[1], MessageRead)
#         assert messages[1].message == "How are you?"
#         assert messages[1].media_file_url == "http://test2.com/test2.jpg"
#         assert messages[1].email == "test2@mail.com"


async def test_get_messages_in_room_room_is_empty(mock_db_session):
    # Мокаем результат запроса к базе данных
    mock_db_session.execute.return_value.fetchall.return_value = []

    # Вызываем функцию, которую тестируем
    messages = await get_messages_in_room(mock_db_session, 2)

    # Проверяем, что она вернула пустой список
    assert len(messages) == 0


async def test_get_members_in_room_room_is_empty(mock_db_session):
    # Мокаем результат запроса к базе данных
    mock_db_session.execute.return_value.fetchall.return_value = []

    # Вызываем функцию, которую тестируем
    members = await get_members_in_room(mock_db_session, 1)

    # Проверяем, что она вернула пустой список
    assert len(members) == 0
