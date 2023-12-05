import logging
from typing import List

from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from room.crud import set_room_activity

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, session: AsyncSession, websocket: WebSocket, room_name: str):
        await websocket.accept()
        await set_room_activity(session, room_name, True)
        self.active_connections.append(websocket)

    async def disconnect(self, session: AsyncSession, websocket: WebSocket, room_name: str):
        await set_room_activity(session, room_name, False)
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, chat_history_dict):
        logger.debug(f"Broadcasting across {len(self.active_connections)} CONNECTIONS")
        for connection in self.active_connections:
            await connection.send_json({"messages": chat_history_dict})
            logger.debug(f"Broadcasting: {chat_history_dict}")
