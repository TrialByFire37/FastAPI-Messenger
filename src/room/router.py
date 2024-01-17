from fastapi import APIRouter, Depends, Request

from auth.base_config import fastapi_users
from auth.schemas import UserRead
from database import get_async_session
from ratelimiter import limiter
from room.crud import *
from room.schemas import RoomCreateRequest, FavoriteRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/room")
@limiter.limit("5/minute")
async def create_room(request: Request,
                      createrequest: RoomCreateRequest,
                      current_user: UserRead = Depends(fastapi_users.current_user()),
                      session: AsyncSession = Depends(get_async_session)):
    """
    Create a room
    """
    res = await insert_room(session, current_user.username, createrequest.room_name)
    return res


@router.put("/room/{room_name}")
@limiter.limit("5/minute")
async def add_user_to_room_members(request: Request,
                                   room_name: str,
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
    rooms = await get_rooms(session, current_user.id, page, limit)
    return rooms


@router.get("/rooms/{room_name}")
async def filter_out_rooms(room_name: str, page: int = 1, limit: int = 10,
                        current_user: UserRead = Depends(fastapi_users.current_user()),
                        session: AsyncSession = Depends(get_async_session)):
    """
    Filter all rooms
    """
    rooms = await filter_rooms(session, current_user.id, room_name, page, limit)
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
    rooms = await get_user_favorite(session, current_user.id)
    return rooms


@router.post("/favorite")
@limiter.limit("5/minute")
async def alter_favorite_room(request: Request,
                              favrequest: FavoriteRequest,
                              session: AsyncSession = Depends(get_async_session),
                              current_user: UserRead = Depends(fastapi_users.current_user())):
    """
    Add or remove a favorite room from a user
    the request.is_chosen should be either "true" or "false"
    """
    row = await alter_favorite(session, current_user.id, favrequest)
    return row
