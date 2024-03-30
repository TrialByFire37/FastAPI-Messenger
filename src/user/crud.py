import logging
from typing import List, Optional

from fastapi import UploadFile
from fastapi_users.password import PasswordHelper
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserRead
from aws.service import upload, get_url
from models.models import user, room_user
from user.schemas import UserReadRequest, UserBaseReadRequest, UserUpdateRequest

logger = logging.getLogger(__name__)


async def get_user_by_id(session: AsyncSession, user_id: int) -> UserReadRequest:
    try:
        user_instance = (await session.execute(select(user).filter_by(id=user_id))).one()
        await session.commit()
        return UserReadRequest(
            user_id=user_instance.id,
            username=user_instance.username,
            email=user_instance.email,
            profile_pic_img_src=user_instance.image_url
        )
    except NoResultFound as e:
        logger.error(f"Error getting user by ID: {e}")
        return None


async def get_user_by_username(session: AsyncSession, username: str) -> UserReadRequest:
    try:
        user_instance = (await session.execute(select(user).filter_by(username=username))).one()
        await session.commit()
        return UserReadRequest(
            user_id=user_instance.user_id,
            username=user_instance.username,
            email=user_instance.email,
            profile_pic_img_src=user_instance.image_url
        )
    except NoResultFound as e:
        logger.error(f"Error getting user by name: {e}")
        return None


async def get_users_in_room(session: AsyncSession, room_id: int) -> List[UserReadRequest]:
    result = await session.execute(
        select(user)
        .join(room_user, user.c.id == room_user.c.user)
        .where(room_user.c.room == room_id)
    )
    rows = result.fetchall()
    users: List[UserReadRequest] = list()
    for row in rows:
        users.append(UserReadRequest(
            user_id=row[0],
            username=row[1],
            email=row[2],
            image_url=row[4]
        ))
    await session.commit()
    return users


async def update_user_image(
        session: AsyncSession, current_user: UserRead, file: Optional[UploadFile]
) -> Optional[UserBaseReadRequest]:
    try:
        file_to_name = await upload(file)
        image_url = await get_url(file_to_name.file_name)
        await session.execute(
            update(user)
            .where(user.c.id == current_user.id)
            .values(image_url=image_url))
        await session.commit()
        return UserBaseReadRequest(user_id=current_user.id, username=current_user.username,
                                   image_url=current_user.image_url)
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        await session.rollback()
        return None
