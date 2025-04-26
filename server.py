from typing import Dict, Set

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections per session
connections: Dict[str, Set[WebSocket]] = {}

# Store usernames per session
users: Dict[str, Dict[WebSocket, str]] = {}

async def broadcast_message(session_id: str, message: dict, exclude_websocket: WebSocket = None):
    """Broadcast a message to all connections in a session except the sender"""
    if session_id in connections:
        for connection in connections[session_id]:
            if connection != exclude_websocket:
                await connection.send_json(message)

@app.get("/")
async def root():
    return {"message": "WebSocket Chat Server"}

@app.websocket("/ws/{session_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, username: str):
    await websocket.accept()
    
    # Initialize session if it doesn't exist
    if session_id not in connections:
        connections[session_id] = set()
        users[session_id] = {}
    
    # Add connection to session
    connections[session_id].add(websocket)
    users[session_id][websocket] = username
    
    # Announce user joined
    await broadcast_message(
        session_id,
        {
            "type": "system",
            "content": f"{username} joined the chat"
        },
        websocket
    )
    
    try:
        while True:
            # Receive and broadcast message
            data = await websocket.receive_json()
            message = {
                "type": "message",
                "username": username,
                "content": data["content"]
            }
            # Broadcast to others
            await broadcast_message(session_id, message, websocket)
            # Send back to sender
            await websocket.send_json(message)
            
    except WebSocketDisconnect:
        # Remove connection
        connections[session_id].remove(websocket)
        del users[session_id][websocket]
        
        # Remove session if empty
        if not connections[session_id]:
            del connections[session_id]
            del users[session_id]
        else:
            # Announce user left
            await broadcast_message(
                session_id,
                {
                    "type": "system",
                    "content": f"{username} left the chat"
                }
            )

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8765, reload=True)
