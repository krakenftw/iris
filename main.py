import asyncio
import json

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


async def start_chat():
    console.print("[bold green]Welcome to Global Chat App![/bold green]")

    # Get username from user
    username = Prompt.ask("[yellow]Enter your username[/yellow]")

    console.print("[green]Connecting to chat...[/green]")

    # Connect to WebSocket server
    uri = f"ws://localhost:8765/ws/{username}"
    console.print("[yellow]Connected to chat. Press Ctrl+C to exit.[/yellow]")

    try:
        async with websockets.connect(uri) as websocket:
            await asyncio.gather(receive_messages(websocket), send_messages(websocket))
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    try:

        async def main():
            await asyncio.gather(start_server(), start_chat())

        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[red]Chat session ended[/red]")
