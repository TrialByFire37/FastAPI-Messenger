import pytest

from conftest import async_session_maker
from message.crud import upload_message_to_room


# async def upload_message_to_room(session: AsyncSession, room_name: str, user_name: str, message_data: str):
#     try:
#         room_id = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
#         user_id = (await session.execute(select(user).filter_by(username=user_name))).scalar_one()
#         await session.execute(insert(message).values(message_data=message_data, user=user_id, room=room_id))
#         await session.commit()
#         return True
#     except Exception as e:
#         logger.error(f"Error adding message to DB: {type(e)} {e}")
#         await session.rollback()
#         return False

@pytest.mark.parametrize("username, room_name, message", [
    ("four123f", "string1", "Hello, World!"),
])
async def test_upload_message_to_room(username, room_name, message):
    async with async_session_maker() as session:
        await upload_message_to_room(session, room_name, username, message)


@pytest.mark.parametrize("username, room_name, message", [
    ("four123f1", "string1", "Hello, World!"),
])
async def test_upload_message_to_room_fail(username, room_name, message):
    async with async_session_maker() as session:
        value = await upload_message_to_room(session, room_name, username, message)
        assert value is False

