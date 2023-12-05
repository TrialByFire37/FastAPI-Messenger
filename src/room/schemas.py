from typing import Optional, List

from pydantic import BaseModel, Field

from message.schemas import MessageRead
from user.schemas import UserReadRequest


class RoomBaseRequest(BaseModel):
    room_name: str


class RoomCreateRequest(RoomBaseRequest):
    pass


class RoomBaseInfoRequest(RoomBaseRequest):
    room_id: int


class RoomBaseInfoForUserRequest(RoomBaseInfoRequest):
    is_favorites: bool


class RoomReadRequest(RoomBaseInfoRequest):
    pass


class FavoriteRequest(BaseModel):
    room_name: str
    is_chosen: bool
