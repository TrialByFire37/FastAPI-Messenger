# import json
# import logging
#
# from fastapi import WebSocket, APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from starlette.websockets import WebSocketState
#
# from database import get_async_session
# from notifier import ConnectionManager
# from room.crud import get_room_by_name, add_user_to_room, remove_user_from_room
#
# router = APIRouter(
#
# )
#
# manager = ConnectionManager()
#
#
# @router.websocket("/ws/{room_name}/{user_name}")
# async def websocket_endpoint(websocket: WebSocket, room_name, user_name):
#     try:
#         # add user
#         session: AsyncSession = Depends(get_async_session)
#         await manager.connect(websocket, room_name)
#         await add_user_to_room(user_name, room_name)
#         room = await get_room_by_name(session, room_name)
#         data = {
#             "content": f"{user_name} has entered the chat",
#             "user": {"username": user_name},
#             "room_name": room_name,
#             "type": "entrance",
#             "new_room_obj": room,
#         }
#         await manager.broadcast(f"{json.dumps(data, default=str)}")
#         # wait for messages
#         while True:
#             if websocket.application_state == WebSocketState.CONNECTED:
#                 data = await websocket.receive_text()
#                 message_data = json.loads(data)
#                 if "type" in message_data and message_data["type"] == "dismissal":
#                     logging.warning(message_data["content"])
#                     logging.info("Disconnecting from Websocket")
#                     await manager.disconnect(websocket, room_name)
#                     break
#                 else:
#                     await upload_message_to_room(data)
#                     logging.info(f"DATA RECIEVED: {data}")
#                     await manager.broadcast(f"{data}")
#             else:
#                 logging.warning(f"Websocket state: {websocket.application_state}, reconnecting...")
#                 await manager.connect(websocket, room_name)
#     except Exception as ex:
#         template = "An exception of type {0} occurred. Arguments:\n{1.txt!r}"
#         message = template.format(type(ex).__name__, ex.args)
#         logging.error(message)
#         # remove user
#         logging.warning("Disconnecting Websocket")
#         await remove_user_from_room(None, room_name, username=user_name)
#         room = await get_room_by_name(room_name)
#         data = {
#             "content": f"{user_name} has left the chat",
#             "user": {"username": user_name},
#             "room_name": room_name,
#             "type": "dismissal",
#             "new_room_obj": room,
#         }
#         await manager.broadcast(f"{json.dumps(data, default=str)}")
#         await manager.disconnect(websocket, room_name)
