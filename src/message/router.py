import json
import logging

from fastapi import WebSocket, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketState, WebSocketDisconnect

from database import get_async_session
from message.crud import upload_message_to_room
from message.notifier import ConnectionManager
from room.crud import set_user_room_activity, get_room, add_user_to_room
from user.crud import get_user_by_username

logger = logging.getLogger(__name__)

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/{room_name}/{user_name}")
async def websocket_endpoint(
        websocket: WebSocket,
        room_name: str,
        user_name: str,
        session: AsyncSession = Depends(get_async_session)
):
    # Connect the user to the WebSocket
    await manager.connect(session, websocket, room_name)
    is_new = await add_user_to_room(session, user_name, room_name)
    if is_new is False:
        await set_user_room_activity(session, user_name, room_name, True)
    room = await get_room(session, room_name)
    data = {
        "content": f"{user_name} has entered the chat",
        "user": {"username": user_name},
        "room_name": room_name,
        "type": "entrance",
        "new_room_obj": {
            "room_id": room.room_id,
            "room_name": room_name,
            "members": room.members,
            "messages": room.messages,
            "active": room.room_active,
            "date_created": room.room_creation_date
        },
    }
    await manager.broadcast(f"{json.dumps(data, default=str)}")
    # wait for messages
    try:
        while True:
            if websocket.application_state == WebSocketState.CONNECTED:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                await upload_message_to_room(session, room_name, user_name, message_data["content"])
                logger.info(f"DATA RECIEVED: {data}")
                await manager.broadcast(f"{data}")
    except WebSocketDisconnect as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logger.error(message)
        logger.warning("Disconnecting Websocket")
        await set_user_room_activity(session, user_name, room_name, False)
        await manager.disconnect(session, websocket, room_name)
