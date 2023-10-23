from typing import Optional

from pydantic import BaseModel


class UserBaseReadRequest(BaseModel):
    user_id: int
    username: str
    image_url: Optional[str]


class UserReadRequest(UserBaseReadRequest):
    email: str


class UserImageUploadRequest(BaseModel):
    image_url: str
