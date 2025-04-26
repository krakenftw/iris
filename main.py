import asyncio
import json
import uuid

import dotenv
import websockets
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from server import start_server
from tools.calenders.googlecal.service import GoogleCalendarService
from tools.linear.service import LinearService

dotenv.load_dotenv()

linear_service = LinearService()
calendar_service = GoogleCalendarService()

console = Console()

# Global dictionary to track active sessions
active_sessions = {}


class Session(BaseModel):
    id: str
    users: list[str] = []


class Message(BaseModel):
    type: str
    username: str
    content: str


async def receive_messages(websocket, session_id, username):
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data["type"] == "system":
                console.print(f"[yellow]{data['content']}[/yellow]")
            else:
                console.print(
                    Panel(
                        data["content"],
                        title=f"[blue]{data['username']}[/blue]",
                        border_style="blue",
                    )
                )
    except websockets.exceptions.ConnectionClosed:
        console.print("[red]Connection closed[/red]")
        # Remove user from session when disconnected
        if (
            session_id in active_sessions
            and username in active_sessions[session_id].users
        ):
            active_sessions[session_id].users.remove(username)
            # If session is empty, remove it
            if not active_sessions[session_id].users:
                del active_sessions[session_id]


async def send_messages(websocket):
    try:
        while True:
            content = await asyncio.get_event_loop().run_in_executor(
                None, lambda: Prompt.ask("You")
            )
            await websocket.send(json.dumps({"content": content}))
    except KeyboardInterrupt:
        pass


async def create_new_group():
    # Generate a random session ID for a new group
    session_id = str(uuid.uuid4())
    console.print(
        f"[green]Group created! Share this invitation link with others:[/green]"
    )
    console.print(f"[bold cyan]http://localhost:8765/ws/{session_id}[/bold cyan]")

    # Create a new session and store it in the active sessions dictionary
    active_sessions[session_id] = Session(id=session_id)

    return session_id


async def join_group(invitation_link):
    # Extract session ID from invitation link
    try:
        if "/ws/" in invitation_link:
            session_id = invitation_link.split("/ws/")[1].strip()

            # Add the session to our active sessions if it's not already there
            if session_id not in active_sessions:
                active_sessions[session_id] = Session(id=session_id)

            return session_id
        else:
            console.print("[red]Invalid invitation link format[/red]")
            return None
    except Exception as e:
        console.print(f"[red]Error joining group: {str(e)}[/red]")
        return None


async def main():
    asyncio.create_task(start_server())
    console.print("[bold green]Welcome to Group Chat App![/bold green]")
    console.print("Select an option:")
    console.print("1. Create a new group")
    console.print("2. Join an existing group")

    choice = Prompt.ask("Enter your choice", choices=["1", "2"])

    session_id = None
    if choice == "1":
        session_id = await create_new_group()
    else:
        invitation_link = Prompt.ask("Paste the invitation link to join")
        session_id = await join_group(invitation_link)
        if not session_id:
            console.print("[red]Failed to join group. Exiting...[/red]")
            return

    # Get username from user
    username = Prompt.ask("[yellow]Enter your username[/yellow]")

    # Add user to the session
    if session_id in active_sessions:
        active_sessions[session_id].users.append(username)

    console.print(f"[green]Connecting to group {session_id}...[/green]")

    # Connect to WebSocket server
    uri = f"ws://localhost:8765/ws/{session_id}/{username}"
    console.print("[yellow]Connecting to chat. Press Ctrl+C to exit.[/yellow]")

    try:
        async with websockets.connect(uri) as websocket:
            await asyncio.gather(
                receive_messages(websocket, session_id, username),
                send_messages(websocket),
            )
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        # Handle disconnection - remove user from session
        if (
            session_id in active_sessions
            and username in active_sessions[session_id].users
        ):
            active_sessions[session_id].users.remove(username)
            # If session is empty, remove it
            if not active_sessions[session_id].users:
                del active_sessions[session_id]


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[red]Chat session ended[/red]")
