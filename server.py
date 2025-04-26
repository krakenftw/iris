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

# Store all active connections
connections: Set[WebSocket] = set()

# Store usernames per connection
user_names: Dict[WebSocket, str] = {}


async def broadcast_message(message: dict, exclude_websocket: WebSocket = None):
    """Send a message to all connections except the sender"""
    for connection in connections:
        if connection != exclude_websocket:
            await connection.send_json(message)


@app.get("/")
async def root():
    return {"message": "WebSocket Chat Server"}


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()

    # Add connection to the global set
    connections.add(websocket)
    user_names[websocket] = username

    # Announce user joined
    await broadcast_message(
        {"type": "system", "content": f"{username} joined the chat"},
        exclude_websocket=None,  # Send to everyone including the user who joined
    )

    try:
        # Listen for messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Create message with username
            message = {
                "type": "message",
                "username": username,
                "content": data["content"],
            }

            # Broadcast to all users except sender
            await broadcast_message(message, exclude_websocket=websocket)

            # Send back to sender as well
            await websocket.send_json(message)

    except WebSocketDisconnect:
        # Clean up when user disconnects
        connections.remove(websocket)

        if websocket in user_names:
            username = user_names[websocket]
            del user_names[websocket]

            # Notify others that user left
            await broadcast_message(
                {"type": "system", "content": f"{username} left the chat"}
            )


async def start_server():
    config = uvicorn.Config("server:app", host="0.0.0.0", port=8765, reload=False)
    server = uvicorn.Server(config)
    await server.serve()
