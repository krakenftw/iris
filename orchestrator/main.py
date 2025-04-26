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

    def process(self, message: str):
        print(f"Processing message: {message}")
