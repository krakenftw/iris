# Group Chat App

A simple terminal-based group chat application using WebSockets.

## Features
- Create a new chat room
- Join existing rooms via invitation links
- Room-based chat system - users with the same room ID are in the same room
- Real-time messaging with all room members
- Terminal-based interface with rich formatting

## Setup
1. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage
1. Run the application:
```
python main.py
```

2. Choose one of the options:
   - Create a new room: Gets a shareable invitation link
   - Join an existing room: Paste the invitation link
     - All users with the same room ID will be in the same chat room

3. Enter your username when prompted

4. Start chatting! Press Ctrl+C to exit.

## How It Works
- The server and client run in the same process
- The application uses WebSockets for real-time communication
- Each room has a unique ID that's part of the invitation link
- The server tracks all connected users in each room
- When a message is sent, it's broadcast to all users in the same room
- When all users leave a room, it's automatically cleaned up
