from fastapi import APIRouter, Depends

from auth.base_config import fastapi_users
from database import get_async_session
from user.crud import *

router = APIRouter()


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
