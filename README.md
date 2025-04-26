# Group Chat App

A simple terminal-based group chat application using WebSockets.

## Features
- Create a new group
- Join existing groups via invitation links
- Real-time messaging with all group members
- Terminal-based interface with rich formatting

## Setup
1. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage
1. Start the server (keep this running in a separate terminal):
```
python server.py
```

2. Run the client application:
```
python main.py
```

3. Choose one of the options:
   - Create a new group: Gets a shareable invitation link
   - Join an existing group: Paste the invitation link

4. Enter your username when prompted

5. Start chatting! Press Ctrl+C to exit.

## How It Works
- The application uses WebSockets for real-time communication
- Each group has a unique session ID that's part of the invitation link
- Messages are broadcast to all members of the same group
