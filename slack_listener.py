from tools.slack.service import SlackService
from ai_team_processor import AITeamInteractor
import dotenv
import os
import time
import signal
import sys
from rich.console import Console

# Initialize console for pretty output
console = Console()

# Load environment variables
dotenv.load_dotenv()

def handle_exit(signal, frame):
    """Handle exit signals gracefully"""
    console.print("\n[bold yellow]Shutting down Slack listener...[/bold yellow]")
    if slack_service and hasattr(slack_service, 'socket_client'):
        slack_service.close_connection()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def process_slack_message(channel_id, user_id, text, event_data):
    """Process incoming Slack messages
    
    Args:
        channel_id: ID of the channel where the message was posted
        user_id: ID of the user who sent the message
        text: Content of the message
        event_data: Full event data from Slack
    """
    console.print(f"[bold blue]Received message:[/bold blue] {text}")
    
    # Only process messages that might be task requests
    task_keywords = ["create", "schedule", "task", "meeting", "assign", "urgent", "important"]
    
    if any(keyword in text.lower() for keyword in task_keywords):
        console.print("[bold green]Detected potential task request![/bold green]")
        
        # Process the message with AI team interactor
        result = ai_interactor.process_message(text)
        
        if result["understood"]:
            console.print("[bold green]Successfully processed the request![/bold green]")
            
            # Format response
            response_text = "I've processed your request!"
            
            # Create task_info dictionary for formatting
            task_info = {
                "title": result.get("issue", {}).get("title", "Task") if result.get("issue") else "Task",
                "description": result.get("issue", {}).get("description", "No description") if result.get("issue") else "",
                "assignee": result.get("issue", {}).get("assignee", {}).get("name", "Unassigned") if result.get("issue") and result.get("issue").get("assignee") else "Unassigned",
                "priority": "Urgent" if result.get("issue", {}).get("priority", 0) >= 3 else "Normal",
                "url": result.get("issue", {}).get("url") if result.get("issue") else None
            }
            
            # Add meeting info if available
            if result.get("meeting"):
                task_info["meeting"] = {
                    "time": result.get("meeting", {}).get("start", "Not specified"),
                    "link": result.get("meeting", {}).get("link", "")
                }
            
            # Format blocks for rich message
            blocks = slack_service.format_task_message(task_info)
            
            # Send response
            slack_service.send_message(
                channel=channel_id,
                text=response_text,
                blocks=blocks
            )
        else:
            console.print("[bold yellow]Couldn't understand the request.[/bold yellow]")
            slack_service.send_message(
                channel=channel_id,
                text="I'm not sure I understood your request. Could you provide more details about the task or meeting you want to create?"
            )

def main():
    """Main function to run the Slack listener"""
    console.print("[bold green]Starting Slack listener...[/bold green]")
    
    if not os.environ.get('SLACK_BOT_TOKEN') or not os.environ.get('SLACK_APP_TOKEN'):
        console.print("[bold red]Error: SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in environment variables[/bold red]")
        console.print("Please add these to your .env file or export them in your shell.")
        return
    
    try:
        # Initialize the Slack service
        global slack_service
        slack_service = SlackService()
        
        # Initialize the AI Team Interactor
        global ai_interactor
        ai_interactor = AITeamInteractor()
        
        console.print("[bold green]Services initialized successfully![/bold green]")
        console.print("[bold blue]Connecting to Slack...[/bold blue]")
        
        # Start listening for messages
        client = slack_service.listen_for_messages(process_slack_message)
        
        console.print("[bold green]Connected to Slack! Listening for messages...[/bold green]")
        console.print("[italic](Press Ctrl+C to exit)[/italic]")
        
        # Keep the program running
        while True:
            time.sleep(1)
            
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        
        if "cannot use socket mode" in str(e).lower() or "invalid_auth" in str(e).lower():
            console.print("\n[bold yellow]Authentication Error:[/bold yellow]")
            console.print("1. Make sure your SLACK_BOT_TOKEN and SLACK_APP_TOKEN are correct")
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