import os
import signal
import sys
import time

import dotenv
from rich.console import Console
from tools.tools import ToolCallingLayer
from datetime import datetime
from orchestrator.main import Orchestrator
from tools.slack.service import SlackService

# Initialize console for pretty output
console = Console()

# Load environment variables
dotenv.load_dotenv()

tool_layer = ToolCallingLayer()


def handle_exit(signal, frame):
    slack_service.close_connection()    
    sys.exit(0)
    """Handle exit signals gracefully"""
    console.print("\n[bold yellow]Shutting down Slack listener...[/bold yellow]")
    if slack_service and hasattr(slack_service, "socket_client"):
        slack_service.close_connection()
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

orchestrator = Orchestrator()


def process_slack_message(channel_id, user_id, text, event_data):
    console.print(f"[bold blue]Received message:[/bold blue] {text}")
    # orchestrator.process(text)
    tool_layer.process_query(text,f"You are a helpful assistant that can use tools to help the user. your tools include slack, google calendar, linear, and calculator. you can use these tools to help the user with their questions. you can also use the tools to help the user with their tasks. you can call multiple tools at once if needed. Todays date is {datetime.now().strftime('%Y-%m-%d')}")


def main():
    """Main function to run the Slack listener"""
    console.print("[bold green]Starting Slack listener...[/bold green]")

    if not os.environ.get("SLACK_BOT_TOKEN") or not os.environ.get("SLACK_APP_TOKEN"):
        console.print(
            "[bold red]Error: SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in environment variables[/bold red]"
        )
        console.print(
            "Please add these to your .env file or export them in your shell."
        )
        return

    try:
        # Initialize the Slack service
        global slack_service
        slack_service = SlackService()

        console.print("[bold green]Services initialized successfully![/bold green]")
        console.print("[bold blue]Connecting to Slack...[/bold blue]")

        # Start listening for messages
        client = slack_service.listen_for_messages(process_slack_message)

        console.print(
            "[bold green]Connected to Slack! Listening for messages...[/bold green]"
        )
        console.print("[italic](Press Ctrl+C to exit)[/italic]")

        # Keep the program running
        while True:
            time.sleep(1)

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")

        if (
            "cannot use socket mode" in str(e).lower()
            or "invalid_auth" in str(e).lower()
        ):
            console.print("\n[bold yellow]Authentication Error:[/bold yellow]")
            console.print(
                "1. Make sure your SLACK_BOT_TOKEN and SLACK_APP_TOKEN are correct"
            )
            console.print("2. Ensure your Slack app has the necessary permissions:")
            console.print("   - chat:write")
            console.print("   - users:read")
            console.print("   - users:read.email")
            console.print("   - channels:read")
            console.print("   - groups:read")
            console.print("   - im:read")
            console.print("   - mpim:read")
            console.print("3. Verify Socket Mode is enabled in your Slack app settings")


if __name__ == "__main__":
    main()
