import asyncio
import json
import uuid

import dotenv
import websockets
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


async def receive_messages(websocket):
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


async def send_messages(websocket):
    try:
        while True:
            content = await asyncio.get_event_loop().run_in_executor(
                None, lambda: Prompt.ask("You")
            )
            await websocket.send(json.dumps({"content": content}))
    except KeyboardInterrupt:
        pass


async def create_new_room():
    # Generate a random room ID
    room_id = str(uuid.uuid4())
    console.print(
        f"[green]Room created! Share this invitation link with others:[/green]"
    )
    console.print(f"[bold cyan]http://localhost:8765/ws/{room_id}[/bold cyan]")
    return room_id


async def join_room(invitation_link):
    # Extract room ID from invitation link
    try:
        if "/ws/" in invitation_link:
            room_id = invitation_link.split("/ws/")[1].strip()
            return room_id
        else:
            console.print("[red]Invalid invitation link format[/red]")
            return None
    except Exception as e:
        console.print(f"[red]Error joining room: {str(e)}[/red]")
        return None


async def start_chat():
    console.print("[bold green]Welcome to Group Chat App![/bold green]")
    console.print("Select an option:")
    console.print("1. Create a new room")
    console.print("2. Join an existing room")

    choice = Prompt.ask("Enter your choice", choices=["1", "2"])

    room_id = None
    if choice == "1":
        room_id = await create_new_room()
    else:
        invitation_link = Prompt.ask("Paste the invitation link to join")
        room_id = await join_room(invitation_link)
        if not room_id:
            console.print("[red]Failed to join room. Exiting...[/red]")
            return

    # Get username from user
    username = Prompt.ask("[yellow]Enter your username[/yellow]")

    console.print(f"[green]Connecting to room {room_id}...[/green]")

    # Connect to WebSocket server
    uri = f"ws://localhost:8765/ws/{room_id}/{username}"
    console.print("[yellow]Connecting to chat. Press Ctrl+C to exit.[/yellow]")

    try:
        async with websockets.connect(uri) as websocket:
            await asyncio.gather(receive_messages(websocket), send_messages(websocket))
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    try:

        async def main():
            tasks = [start_server(), start_chat()]
            await asyncio.gather(*tasks)

        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[red]Chat session ended[/red]")
