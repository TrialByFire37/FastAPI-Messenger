import logging

from fastapi import WebSocket, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketState

from database import get_async_session
from message.crud import get_chat_history, upload_message_to_room
from message.notifier import ConnectionManager
from room.crud import remove_user_from_room, get_room, add_user_to_room
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
    try:
        # Connect the user to the WebSocket
        await manager.connect(session, websocket, room_name)
        await add_user_to_room(session, user_name, room_name)
        room = await get_room(session, room_name)
        sender = await get_user_by_username(session, user_name)

        # Send chat history to the connected user
        chat_history = await get_chat_history(session, room_name)
        chat_history_dict = [jsonable_encoder(message) for message in chat_history]
        data = {
            "content": f"{sender.username} has entered the chat",
            "media_file_url": None,
            "sender": {
                "username": sender.username,
                "image_url": sender.image_url,
                "user_id": sender.user_id,
                "email": sender.email
            },
        }
        chat_history_dict.append(data)
        await manager.broadcast(chat_history_dict)

        while websocket.client_state != WebSocketState.DISCONNECTED:
            message = await websocket.receive_text()
            await handle_message(session, room_name, user_name, message)

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logger.error(message)
        logger.warning("Disconnecting Websocket")
        await remove_user_from_room(session, user_name, room_name)
        await manager.disconnect(session, websocket, room_name)


async def handle_message(session, room_name, user_name, message):
    success = await upload_message_to_room(session, room_name, user_name, message)
    if success:
        # Retrieve the chat history for the room
        chat_history = await get_chat_history(session, room_name)
        chat_history_dict = [jsonable_encoder(message) for message in chat_history]

        # Send the chat history to all connected users
        await manager.broadcast(chat_history_dict)
