from fastapi import APIRouter, Depends

from auth.base_config import fastapi_users
from database import get_async_session
from message.crud import upload_message_with_file_to_room
from user.crud import *
from user.schemas import UserUpdateRequest

router = APIRouter()


@router.put("/update/me")
async def update_me(
        request: UserUpdateRequest,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserRead = Depends(fastapi_users.current_user()),
) -> None:
    """
    Update the current user
    """
    return await update_user_data(session, current_user, request)


@router.get("/get/me")
async def get_me(
        session: AsyncSession = Depends(get_async_session),
        current_user: UserRead = Depends(fastapi_users.current_user()),
):
    """
    Return a current user
    """
    return await get_current_user(session, current_user)


@router.post("/profile_picture")
async def upload_profile_picture(
        file: Optional[UploadFile] = None,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserRead = Depends(fastapi_users.current_user()),
) -> Optional[UserBaseReadRequest]:
    """
    Upload a profile picture for the current user
    """
    return await update_user_image(session, current_user, file)


@router.post("/upload_image")
async def upload_file(
        user_name: str,
        room_name: str,
        file: Optional[UploadFile] = None,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserRead = Depends(fastapi_users.current_user()),
) -> Optional[UserBaseReadRequest]:
    """
    Upload a file to DB (FOR TESTING PURPOSES)
    """
    return await upload_message_with_file_to_room(session, room_name, user_name, file)
