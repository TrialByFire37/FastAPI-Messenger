from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    image_url: Optional[str]


class UserBaseReadRequest(UserBase):
    user_id: int


class UserReadRequest(UserBaseReadRequest):
    email: str


class UserImageUploadRequest(BaseModel):
    image_url: str


class UserUpdateRequest(BaseModel):
    password: str = None
    username: str = None
