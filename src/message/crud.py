import logging
from typing import List

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from message.schemas import MessageRead
from models.models import *
from user.crud import get_user_by_id

logger = logging.getLogger(__name__)


async def upload_message_to_room(session: AsyncSession, room_name: str, user_name: str, message_data: str):
    try:
        room_id = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
        user_id = (await session.execute(select(user).filter_by(username=user_name))).scalar_one()
        await session.execute(insert(message).values(message_data=message_data, user=user_id, room=room_id))
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding message to DB: {type(e)} {e}")
        await session.rollback()
        return False


async def get_chat_history(session: AsyncSession, room_name: str) -> List[MessageRead]:
    room_id = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
    await session.commit()
    messages = await get_messages_in_room(session, room_id)
    return messages

async def get_messages_in_room(session: AsyncSession, room_id: int) -> List[MessageRead]:
    result = await session.execute(
        select(message)
        .join(room, room.c.room_id == message.c.room)
        .where(room.c.room_id == room_id)
    )
    rows = result.fetchall()
    messages: List[MessageRead] = list()
    for row in rows:
        user_read_request = await get_user_by_id(session, row[4])
        messages.append(MessageRead(
            content=row[1],
            media_file_url=row[2],
            sender=user_read_request,
        ))
    await session.commit()
    return messages
