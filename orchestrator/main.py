import asyncio

from rich.console import Console


class Orchestrator:
    """
    Orchestrator is a class that orchestrates the chat.
    It is responsible for receiving messages from the user and sending them to the server.
    It is also responsible for receiving messages from the server and sending them to the user.
    """

    def __init__(self):
        self.console = Console()
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

    def start(self):
        while True:
            message = await self.input_queue.get()
            await self.output_queue.put(message)

    def consume_nonblocking(self, message: str):
        asyncio.create_task(self.consume(message))

    async def consume(self, message: str):
        await self.output_queue.put(message)
