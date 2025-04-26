import asyncio
import json
import uuid
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
import websockets

console = Console()

async def receive_messages(websocket):
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data["type"] == "system":
                console.print(f"[yellow]{data['content']}[/yellow]")
            else:
                console.print(Panel(
                    data["content"],
                    title=f"[blue]{data['username']}[/blue]",
                    border_style="blue"
                ))
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

async def main():
    # Generate a random session ID for a new chat
    session_id = str(uuid.uuid4())
    username = Prompt.ask("[yellow]Enter your username[/yellow]")
    
    # Connect to WebSocket server
    uri = f"ws://localhost:8765/ws/{session_id}/{username}"
    console.print(f"[green]Share this session ID with others:[/green] {session_id}")
    console.print("[yellow]Waiting for messages. Press Ctrl+C to exit.[/yellow]")
    
    async with websockets.connect(uri) as websocket:
        await asyncio.gather(
            receive_messages(websocket),
            send_messages(websocket)
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[red]Chat session ended[/red]")
