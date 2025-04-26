import asyncio
import os

from rich.console import Console

from llm.openai import AzureOpenAIClient


class Orchestrator:
    """
    Orchestrator is a class that orchestrates the chat.
    It is responsible for receiving messages from the user and sending them to the server.
    It is also responsible for receiving messages from the server and sending them to the user.
    """

    def __init__(self):
        self.console = Console()
        self.llm = AzureOpenAIClient(
            model_id="gpt-4o",
            api_version="2024-12-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

    async def start(self):
        while True:
            message = await self.input_queue.get()
            self.consume_nonblocking(message)

    async def consume_nonblocking(self, message: str):
        take_action = await self.take_action(message)
        if take_action:
            tool_calling_prompt = await self.get_tool_calling_prompt(message)
            tool_response = await self.llm.get_response(tool_calling_prompt)
            await self.output_queue.put(tool_response)

    async def take_action(self, message: str):
        pass

    async def get_tool_calling_prompt(self, message: str):
        pass
