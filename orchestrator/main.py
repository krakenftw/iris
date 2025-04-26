import asyncio
import os

from rich.console import Console
import llm
from orchestrator.client import LLMClient

class Orchestrator:
    """
    Orchestrator is a class that orchestrates the chat.
    It is responsible for receiving messages from the user and sending them to the server.
    It is also responsible for receiving messages from the server and sending them to the user.
    """

    def __init__(self):
        self.console = Console()
        self.llm_client = LLMClient()

    def process(self, message: str):
        print(f"Processing message: {message}")
        response = self.llm_client.get_response(
            prompt=message,
            max_tokens=4096
        )
        print(f"Response: {response}")
        return response
