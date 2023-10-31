from typing import Optional

from pydantic import BaseModel

from user.schemas import UserReadRequest


class MessageRead(BaseModel):
    content: str
    media_file_url: Optional[str]
    sender: UserReadRequest
