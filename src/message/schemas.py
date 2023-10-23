from pydantic import BaseModel
from typing import Optional
from user.schemas import UserReadRequest


class MessageRead(BaseModel):
    content: str
    media_file_url: Optional[str]
    user_read_request: UserReadRequest
