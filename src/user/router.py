from fastapi import APIRouter, Depends

from auth.base_config import fastapi_users
from database import get_async_session
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
    return await update_user_username_and_password(session, current_user, request)


@router.post("/profile_picture")
async def upload_profile_picture(
        file: Optional[UploadFile] = None,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserRead = Depends(fastapi_users.current_user()),
) -> Optional[UserBaseReadRequest]:
    """
    Upload a profile picture for the current user
    """
    return await update_user(session, current_user, file)

@router.post("/file_test")
async def upload_file(
        file: Optional[UploadFile] = None,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserRead = Depends(fastapi_users.current_user()),
) -> Optional[UserBaseReadRequest]:
    """
    Upload a file to DB (FOR TESTING PURPOSES)
    """
    return await upload_test(session, current_user, file)
