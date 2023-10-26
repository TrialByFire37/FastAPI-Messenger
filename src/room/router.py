from fastapi import APIRouter, Depends

from auth.base_config import fastapi_users
from database import get_async_session
from room.crud import *
from room.schemas import RoomCreateRequest, FavoriteRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/room")
async def create_room(request: RoomCreateRequest,
                      current_user: UserRead = Depends(fastapi_users.current_user()),
                      session: AsyncSession = Depends(get_async_session)):
    """
    Create a room
    """
    res = await insert_room(session, current_user.username, request.room_name)
    return res


@router.put("/room/{room_name}")
async def add_user_to_room_members(room_name: str,
                                   current_user: UserRead = Depends(fastapi_users.current_user()),
                                   session: AsyncSession = Depends(get_async_session)):
    """
    Add a user to the room's members
    """
    row = await add_user_to_room(session, current_user.username, room_name)
    return row


@router.get("/rooms")
async def get_all_rooms(page: int = 1, limit: int = 10,
                        current_user: UserRead = Depends(fastapi_users.current_user()),
                        session: AsyncSession = Depends(get_async_session)):
    """
    Get all rooms
    """
    rooms = await get_rooms(session, current_user, page, limit)
    return rooms


@router.get("/room/{room_name}", dependencies=[Depends(fastapi_users.current_user())])
async def get_single_room(room_name: str, session: AsyncSession = Depends(get_async_session)):
    """
    Get Room by room name
    """
    selected_room = await get_room(session, room_name)
    return selected_room


@router.get("/favorites")
async def get_favorite_rooms(session: AsyncSession = Depends(get_async_session),
                             current_user: UserRead = Depends(fastapi_users.current_user())):
    """
    Get all favorite Room objects from a user
    """
    rooms = await get_user_favorite(session, current_user)
    return rooms


@router.post("/favorite")
async def alter_favorite_room(request: FavoriteRequest,
                              session: AsyncSession = Depends(get_async_session),
                              current_user: UserRead = Depends(fastapi_users.current_user())):
    """
    Add or remove a favorite room from a user
    the request.type should be either "add" or "remove"
    """
    row = await alter_favorite(session, current_user, request)
    return row
