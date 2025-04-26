import asyncio
from typing import Dict, Set

import uvicorn
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from rich.console import Console

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active rooms with their connections
rooms: Dict[str, Set[WebSocket]] = {}

# Store usernames per connection
user_names: Dict[WebSocket, str] = {}

# Store which room a connection belongs to
connection_rooms: Dict[WebSocket, str] = {}


async def broadcast_to_room(
    room_id: str, message: dict, exclude_websocket: WebSocket = None
):
    """Send a message to all connections in a room except the sender"""
    if room_id in rooms:
        for connection in rooms[room_id]:
            if connection != exclude_websocket:
                await connection.send_json(message)


@app.get("/")
async def root():
    return {"message": "WebSocket Group Chat Server"}


@app.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
    await websocket.accept()

    # Initialize room if it doesn't exist
    if room_id not in rooms:
        rooms[room_id] = set()
        is_new_room = True
    else:
        is_new_room = False

    # Add connection to room
    rooms[room_id].add(websocket)
    user_names[websocket] = username
    connection_rooms[websocket] = room_id

    # Announce user joined
    if is_new_room:
        system_message = {
            "type": "system",
            "content": f"{username} created a new group",
        }
    else:
        system_message = {"type": "system", "content": f"{username} joined the group"}

    await broadcast_to_room(room_id, system_message)

    # try:
    #     # Listen for messages
    #     while True:
    #         # Receive message from client
    #         data = await websocket.receive_json()

    #         # Create message with username
    #         message = {
    #             "type": "message",
    #             "username": username,
    #             "content": data["content"],
    #         }

    #         # Broadcast to room members
    #         await broadcast_to_room(room_id, message)

    # except WebSocketDisconnect:
    #     # Clean up when user disconnects
    #     if websocket in user_names:
    #         username = user_names[websocket]
    #         del user_names[websocket]

    #     if websocket in connection_rooms:
    #         room_id = connection_rooms[websocket]
    #         del connection_rooms[websocket]

    #         if room_id in rooms:
    #             # Remove from room
    #             rooms[room_id].discard(websocket)

    #             # If room is empty, remove it
    #             if not rooms[room_id]:
    #                 del rooms[room_id]
    #             else:
    #                 # Notify others that user left
    #                 await broadcast_to_room(
    #                     room_id,
    #                     {"type": "system", "content": f"{username} left the group"},
    #                 )


async def start_server():
    config = uvicorn.Config("server:app", host="0.0.0.0", port=8765, reload=False)
    server = uvicorn.Server(config)
    await server.serve()
