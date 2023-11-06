import logging
from typing import Optional, List

from sqlalchemy import select, insert, delete, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from message.crud import get_messages_in_room
from models.models import *
from room.schemas import RoomReadRequest, RoomBaseInfoForUserRequest, FavoriteRequest
from user.crud import get_users_in_room

logger = logging.getLogger(__name__)



async def insert_room(session: AsyncSession, username: str, room_name: str) -> RoomReadRequest:
    try:
        await session.execute(insert(room).values(room_name=room_name))
        user_instance = (await session.execute(select(user).filter_by(username=username))).scalar_one()
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
        await session.execute(insert(room_user).values(user=user_instance, room=room_instance))
        await session.commit()
        return await get_room(session, room_name)
    except Exception as e:
        logger.error(f"Error inserting room to DB: {e}")
        await session.rollback()


async def get_room(session: AsyncSession, room_name: str) -> Optional[RoomReadRequest]:
    try:
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).one()
        room_id = room_instance.room_id
        members = await get_users_in_room(session, room_id)
        messages = await get_messages_in_room(session, room_id)
        await session.commit()
        return RoomReadRequest(
            room_id=room_id,
            room_name=room_instance.room_name,
            members=members,
            messages=messages
        )
    except Exception as e:
        logger.error(f"Error getting room: {e}")
        return None


async def add_user_to_room(session: AsyncSession, username: str, room_name: str):
    try:
        user_instance = (await session.execute(select(user).filter_by(username=username))).scalar_one()
        # await session.execute(insert(room).values(room_name=room_name))
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
        association = room_user.insert().values(user=user_instance, room=room_instance)
        await session.execute(association)
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding user to room: {e}")
        await session.rollback()
        return None


async def remove_user_from_room(session: AsyncSession, username: str, room_name: str):
    try:
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
        user_instance = (await session.execute(select(user).filter_by(username=username))).scalar_one()
        await session.execute(
            delete(room_user).where(
                and_(room_user.c.user == user_instance, room_user.c.room == room_instance)
            )
        )
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Error removing user from room: {e}")
        await session.rollback()
        return False


async def set_room_activity(session: AsyncSession, room_name: str, activity_bool: bool):
    try:
        await session.execute(update(room).where(room.c.room_name == room_name).values(is_active=activity_bool))
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).one()
        await session.commit()
        return room_instance
    except Exception as e:
        logger.error(f"Error setting room activity: {e}")
        await session.rollback()
        return None

# todo: переписать что-то не так тут
async def get_rooms(session: AsyncSession, current_user_id: int, page: int = 1, limit: int = 10) -> Optional[
    List[RoomBaseInfoForUserRequest]]:
    try:
        query = await session.execute(
            select(room, room_user)
            .join(room_user, and_(room.c.room_id == room_user.c.room, room_user.c.user == current_user_id),
                  isouter=True)
            .order_by(room_user.c.is_chosen.desc())
            .limit(limit)
            .offset((page - 1) * limit)
        )
        rooms: List[RoomBaseInfoForUserRequest] = list()
        rows = query.fetchall()
        for row in rows:
            rooms.append(
                RoomBaseInfoForUserRequest(
                    room_id=row[0],
                    room_name=row[1],
                    is_favorites=row[5] if row[5] is not None else False
                )
            )
        rooms.sort(key=lambda x: x.is_favorites, reverse=True)
        await session.commit()
        return rooms
    except Exception as e:
        logger.error(f"Error getting rooms: {e}")
        return None


async def get_user_favorite(session: AsyncSession, current_user_id: int, page: int = 1, limit: int = 10) -> Optional[
    List[RoomBaseInfoForUserRequest]]:
    try:
        query = await (session.execute(
            select(room, room_user)
            .join(room_user, and_(room.c.room_id == room_user.c.room, room_user.c.user == current_user_id,
                                  room_user.c.is_chosen == True))
            .order_by(room_user.c.creation_date.desc())
            .limit(limit)
            .offset((page - 1) * limit)
        ))
        rooms = list()
        rows = query.fetchall()
        for row in rows:
            rooms.append(
                RoomBaseInfoForUserRequest(
                    room_id=row[0],
                    room_name=row[1],
                    is_favorites=row[5] if row[5] is not None else False
                )
            )
        await session.commit()
        return rooms
    except Exception as e:
        logger.error(f"Error getting rooms: {e}")
        return None


async def alter_favorite(session: AsyncSession, current_user_id: int, request: FavoriteRequest) -> None:
    try:
        await (session.execute(
            update(room_user)
            .where(and_(room_user.c.user == current_user_id, room_user.c.room == request.room_id))
            .values(is_chosen=request.is_chosen)
            ))
        await session.commit()
    except Exception as e:
        logger.error(f"Error altering room: {e}")
        await session.rollback()
        return None
