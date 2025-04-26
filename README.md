# Global Chat App

A simple terminal-based chat application using WebSockets.

## Features
- Single global chat room for all users
- Real-time messaging with all connected users
- Terminal-based interface with rich formatting
- Username identification for messages

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

2. Enter your username when prompted

3. Start chatting! Press Ctrl+C to exit.

## How It Works
- The server and client run in the same process
- The application uses WebSockets for real-time communication
- All users connect to a single global chat
- When a message is sent, it's broadcast to all other connected users
- Users are notified when others join or leave the chat
