from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from message.schemas import MessageRead
from models.models import *
from user.crud import get_user_by_id


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
            user_read_request=user_read_request,
        ))
    await session.commit()
    return messages
