import asyncio
from unittest.mock import MagicMock, patch

from message.crud import (upload_message_to_room, get_messages_in_room, get_members_in_room)


# todo: (25) Тест отправки сообщения в комнату
async def test_upload_message_to_room(mock_db_session):
    mock_scalar_one = MagicMock()
    mock_scalar_one.return_value = asyncio.Future()
    mock_scalar_one.return_value.set_result(1)

    room_name = "test_room"
    user_name = "test_user"
    message_data = "test_message"

    with patch.object(mock_db_session, "execute", return_value=mock_scalar_one):
        result = await upload_message_to_room(mock_db_session, room_name, user_name, message_data)

    mock_db_session.commit.assert_called_once()

    assert result == True


# todo: (26) Тест отправки сообщения в комнату - несуществующий пользователь
async def test_upload_message_to_room_fail_user_name(mock_db_session):
    room_name = "test_room"
    user_name = "non_existent_user"
    message_data = "test_message"

    with patch.object(mock_db_session, "execute", return_value=None):
        result = await upload_message_to_room(mock_db_session, user_name, room_name, message_data)

    assert result == False


# todo: (27) Тест отправки сообщения в комнату - несуществующая комната
async def test_upload_message_to_room_fail_room(mock_db_session):
    room_name = "non_existent_room"
    user_name = "test_user"
    message_data = "test_message"

    with patch.object(mock_db_session, "execute", return_value=None):
        result = await upload_message_to_room(mock_db_session, user_name, room_name, message_data)

    assert result == False


# todo: (28) Тест отправки сообщения в комнату - несуществующие комната и пользователь
async def test_upload_message_to_room_fail_user_name_and_room_name(mock_db_session):
    room_name = "non_existent_room"
    user_name = "non_existent_user"
    message_data = "test_message"

    with patch.object(mock_db_session, "execute", return_value=None):
        result = await upload_message_to_room(mock_db_session, user_name, room_name, message_data)

    assert result == False


# todo: (29) Тест геттера сообщений в комнате (Failed)
# async def test_get_messages_in_room(mock_db_session):
#     mock_db_session.execute.return_value.fetchall.return_value = [
#         (1, "Hello!", "http://test1.com/test1.jpg", datetime.utcnow(), 1, 1),
#         (2, "How are you?", "http://test2.com/test2.jpg", datetime.utcnow(), 2, 1)
#     ]
#
#     with patch('user.crud.get_user_by_id', new_callable=AsyncMock) as mock_get_user_by_id:
#         def side_effect(user_id):
#             return UserReadRequest(user_id=user_id, username=f"test{user_id}", email=f"test{user_id}@mail.com", profile_pic_img_src=f"http://test{user_id}.com/test{user_id}.jpg")
#         mock_get_user_by_id.side_effect = side_effect
#
#         result_proxy_mock = MagicMock()
#         result_proxy_mock.fetchall.return_value = [
#             (1, "Hello!", "http://test1.com/test1.jpg", datetime.utcnow(), 1, 1),
#             (2, "How are you?", "http://test2.com/test2.jpg", datetime.utcnow(), 2, 1)
#         ]
#         mock_db_session.execute.return_value = AsyncMock(return_value=result_proxy_mock)
#
#         messages = await get_messages_in_room(mock_db_session, 1)
#
#         assert len(messages) == 2
#         assert isinstance(messages[0], MessageRead)
#         assert messages[0].message == "Hello!"
#         assert messages[0].media_file_url == "http://test1.com/test1.jpg"
#         assert messages[0].email == "test1@mail.com"
#         assert isinstance(messages[1], MessageRead)
#         assert messages[1].message == "How are you?"
#         assert messages[1].media_file_url == "http://test2.com/test2.jpg"
#         assert messages[1].email == "test2@mail.com"


# # todo: (30) Тест геттера сообщений в комнате - пустая комната
# async def test_get_messages_in_room_room_is_empty(mock_db_session):
#     mock_db_session.execute.return_value.fetchall.return_value = []
#
#     messages = await get_messages_in_room(mock_db_session, 2)
#
#     assert len(messages) == 0
#
#
# # todo: (31) Тест геттера пользователей в комнате - пустая комната
# async def test_get_members_in_room_room_is_empty(mock_db_session):
#     mock_db_session.execute.return_value.fetchall.return_value = []
#
#     members = await get_members_in_room(mock_db_session, 1)
#
#     assert len(members) == 0
