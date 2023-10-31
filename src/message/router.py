from fastapi import WebSocket, APIRouter, Depends, HTTPException, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketState

from aws.utils import s3_URL, s3_download
from database import get_async_session
from message.crud import get_chat_history, upload_message_to_room
from message.notifier import ConnectionManager

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

    # Send chat history to the connected user
    chat_history = await get_chat_history(session, room_name)
    chat_history_dict = [jsonable_encoder(message) for message in chat_history]
    await manager.broadcast(chat_history_dict)

    try:
        while websocket.client_state != WebSocketState.DISCONNECTED:
            message = await websocket.receive_text()
            await handle_message(session, room_name, user_name, message)

    except WebSocketDisconnect:
        # Handle disconnection and remove the user from the room
        await manager.disconnect(session, websocket, room_name)


async def handle_message(session, room_name, user_name, message):
    # Handle text messages
    if message.startswith("/file "):
        # Handle file upload command
        file_url = await handle_file_upload(session, message[6:])
        message_data = f"File Uploaded: {file_url}"
    else:
        message_data = message

    # Store the message in the database
    success = await upload_message_to_room(session, room_name, user_name, message_data)
    if success:
        # Retrieve the chat history for the room
        chat_history = await get_chat_history(session, room_name)
        chat_history_dict = [jsonable_encoder(message) for message in chat_history]

        # Send the chat history to all connected users
        await manager.broadcast(chat_history_dict)


async def handle_file_upload(session, file_name):
    # Implement your file upload logic
    # Ensure you save the file to S3 and return its URL
    # Example:
    file_data = await get_file_data_from_s3(file_name)
    if file_data:
        file_url = await s3_URL(file_name)
        return file_url
    else:
        raise HTTPException(status_code=400, detail="File not found or uploaded")


async def get_file_data_from_s3(file_name):
    # Implement your logic to retrieve file data from S3
    # Example:
    try:
        file_data = await s3_download(file_name)
        return file_data
    except Exception as e:
        return None
