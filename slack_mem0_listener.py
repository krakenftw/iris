from orchestrator.slack_mem0_adapter import SlackMem0Adapter
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

# Track the adapter globally for clean shutdown
slack_mem0_adapter = None

def handle_exit(signal, frame):
    """Handle exit signals gracefully"""
    console.print("\n[bold yellow]Shutting down Slack-Mem0 listener...[/bold yellow]")
    if slack_mem0_adapter:
        console.print("Storing active conversations before shutdown...")
        slack_mem0_adapter.close()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def main():
    """Main function to run the Slack-Mem0 listener"""
    global slack_mem0_adapter
    
    console.print("[bold green]Starting Slack-Mem0 Memory Integration[/bold green]")
    
    # Check required environment variables
    required_vars = {
        'SLACK_BOT_TOKEN': 'Slack Bot Token (xoxb-...)',
        'SLACK_APP_TOKEN': 'Slack App Token (xapp-...)',
        'MEM0_API_KEY': 'Mem0 API Key'
    }
    
    missing_vars = []
    for var, desc in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"{var} - {desc}")
    
    if missing_vars:
        console.print("[bold red]Missing required environment variables:[/bold red]")
        for var in missing_vars:
            console.print(f"  - {var}")
        console.print("\nPlease add these to your .env file or export them in your shell.")
        return
    
    try:
        # Initialize the Slack-Mem0 adapter
        slack_mem0_adapter = SlackMem0Adapter(
            mem0_api_key=os.environ.get('MEM0_API_KEY'),
            slack_bot_token=os.environ.get('SLACK_BOT_TOKEN'),
            slack_app_token=os.environ.get('SLACK_APP_TOKEN')
        )
        
        console.print("[bold green]Services initialized successfully![/bold green]")
        console.print("[bold blue]Connecting to Slack and Mem0...[/bold blue]")
        
        # Start listening for messages
        client = slack_mem0_adapter.start_listening()
        
        console.print("[bold green]Connected to Slack! Listening for messages and storing in Mem0...[/bold green]")
        console.print("[italic](Press Ctrl+C to exit)[/italic]")
        
        # Keep the program running
        while True:
            time.sleep(1)
            
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        
        if "cannot use socket mode" in str(e).lower() or "invalid_auth" in str(e).lower():
            console.print("\n[bold yellow]Authentication Error:[/bold yellow]")
            console.print("1. Make sure your SLACK_BOT_TOKEN and SLACK_APP_TOKEN are correct")
            console.print("2. Ensure your Slack app has the necessary permissions")
        
        if "mem0" in str(e).lower():
            console.print("\n[bold yellow]Mem0 Error:[/bold yellow]")
            console.print("1. Make sure your MEM0_API_KEY is correct")
            console.print("2. Check that you have access to the Mem0 API")

if __name__ == "__main__":
    main() 