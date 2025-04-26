import asyncio
import os

from rich.console import Console
from orchestrator.client import LLMClient
from tools.tools import ToolCallingLayer

class Orchestrator:
    """
    Orchestrator is a class that orchestrates the chat.
    It is responsible for receiving messages from the user and sending them to the server.
    It is also responsible for receiving messages from the server and sending them to the user.
    """

    def __init__(self):
        self.console = Console()
        self.llm_client = LLMClient()
        self.tool_layer = ToolCallingLayer()

    def process(self, message: str):
        print(f"Processing message: {message}")
        
        system_prompt = "You are a helpful assistant. Use available tools when appropriate."
        
        # Process the message through ToolCallingLayer to handle tool calls
        result = self.tool_layer.process_query(
            user_prompt=message,
            system_prompt=system_prompt
        )
        
        # Check if a tool was called
        if result.get("tool_called", False):
            # Format tool results for display
            tool_output = ""
            for tool_result in result.get("tool_results", []):
                tool_name = tool_result.get("tool")
                if tool_name == "slack_send_message":
                    channel = tool_result.get("args", {}).get("channel", "")
                    msg_content = tool_result.get("args", {}).get("message", "")
                    tool_output += f"Sent to {channel}: {msg_content}\n"
                else:
                    tool_output += f"{tool_result.get('result')}\n"
            
            response = f"{result.get('result')}\n{tool_output}".strip()
        else:
            # Normal response without tool calls
            response = result.get("result", "")
        
        print(f"Response: {response}")
        return response
