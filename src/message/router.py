import json
import logging

from fastapi import WebSocket, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketState

from message.notifier import ConnectionManager
from database import get_async_session
from room.crud import add_user_to_room, remove_user_from_room, get_room, upload_message_to_room

router = APIRouter()
logger = logging.getLogger(__name__)
manager = ConnectionManager()

# todo: переписать!
@router.websocket("/ws/{room_name}/{user_name}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, user_name: str,
                             session: AsyncSession = Depends(get_async_session)) -> None:
    try:
        # add user
        await manager.connect(session, websocket, room_name)
        await add_user_to_room(session, user_name, room_name)
        room = await get_room(session, room_name)
        data = {
            "content": f"{user_name} has entered the chat",
            "user": {"username": user_name},
            "room_name": room_name,
            "type": "entrance",
            "new_room_obj": room,
        }
        await manager.broadcast(f"{json.dumps(data, default=str)}")
        # wait for messages
        while True:
            if websocket.application_state == WebSocketState.CONNECTED:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                if "type" in message_data and message_data["type"] == "dismissal":
                    logger.warning(message_data["content"])
                    logger.info("Disconnecting from Websocket")
                    await manager.disconnect(session, websocket, room_name)
                    break
                else:
                    await upload_message_to_room(session, data)
                    logger.info(f"DATA RECEIVED: {data}")
                    await manager.broadcast(f"{data}")
            else:
                logger.warning(f"Websocket state: {websocket.application_state}, reconnecting...")
                await manager.connect(session, websocket, room_name)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logger.error(message)
        # remove user
        logger.warning("Disconnecting Websocket")
        await remove_user_from_room(session, user_name, room_name)
        room = await get_room(session, room_name)
        data = {
            "content": f"{user_name} has left the chat",
            "user": {"username": user_name},
            "room_name": room_name,
            "type": "dismissal",
            "new_room_obj": room,
        }
        await manager.broadcast(f"{json.dumps(data, default=str)}")
        await manager.disconnect(session, websocket, room_name)
