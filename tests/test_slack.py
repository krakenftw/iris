from tools.slack.service import SlackService
import dotenv
import os
from rich.console import Console
import time

# Initialize console for pretty output
console = Console()

# Load environment variables
dotenv.load_dotenv()

def test_slack_basic_functionality():
    """Test basic Slack functionality like sending messages"""
    console.print("[bold green]Testing Slack Integration[/bold green]")
    
    if not os.environ.get('SLACK_BOT_TOKEN'):
        console.print("[bold red]Error: SLACK_BOT_TOKEN must be set in environment variables[/bold red]")
        console.print("Please add it to your .env file or export it in your shell.")
        return False
    
    try:
        # Initialize the Slack service
        console.print("\n[bold blue]Initializing Slack service...[/bold blue]")
        slack_service = SlackService()
        console.print("✅ Slack service initialized successfully")
        
        # Get a channel to post to
        channel = input("\nEnter a channel name to post to (e.g., #general): ").strip()
        if not channel:
            channel = "#general"  # Default channel
        
        # Get test user by email (optional)
        test_user_email = input("\nEnter an email to test user lookup (optional): ").strip()
        if test_user_email:
            console.print(f"\n[bold blue]Looking up user by email: {test_user_email}[/bold blue]")
            user = slack_service.get_user_by_email(test_user_email)
            if user:
                console.print(f"✅ Found user: {user.get('real_name')} (ID: {user.get('id')})")
            else:
                console.print("❌ User not found")
        
        # Post a test message
        console.print(f"\n[bold blue]Sending message to {channel}...[/bold blue]")
        
        # Create a sample task info
        task_info = {
            "title": "Test Task from Iris",
            "description": "This is a test task created by Iris to demonstrate Slack integration",
            "assignee": "Test User",
            "priority": "High",
            "url": "https://example.com/task/123",
            "meeting": {
                "time": "Tomorrow at 10:00 AM",
                "link": "https://meet.google.com/test"
            }
        }
        
        # Format the message with Block Kit
        blocks = slack_service.format_task_message(task_info)
        
        # Send the message
        response = slack_service.send_message(
            channel=channel,
            text="Iris - test message with task information",
            blocks=blocks
        )
        
        if response and response['ok']:
            console.print("✅ Message sent successfully!")
            console.print(f"Channel: {response.get('channel')}")
            console.print(f"Timestamp: {response.get('ts')}")
            
            # Wait a moment before trying to update
            time.sleep(1)
            
            # Test sending a follow-up in a thread
            console.print("\n[bold blue]Sending a follow-up in thread...[/bold blue]")
            thread_ts = response.get('ts')
            
            thread_response = slack_service.send_message(
                channel=channel,
                text="This is a follow-up message in the thread",
                thread_ts=thread_ts
            )
            
            if thread_response and thread_response['ok']:
                console.print("✅ Thread message sent successfully!")
            else:
                console.print("❌ Failed to send thread message")
        else:
            console.print("❌ Failed to send message")
        
        console.print("\n[bold green]Slack tests completed![/bold green]")
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        
        if "invalid_auth" in str(e).lower():
            console.print("\n[bold yellow]Authentication Error:[/bold yellow]")
            console.print("1. Make sure your SLACK_BOT_TOKEN is correct")
            console.print("2. Ensure your Slack app has the necessary permissions:")
            console.print("   - chat:write")
            console.print("   - users:read")
            console.print("   - users:read.email")
        
        return False

def test_socket_mode():
    """Test Slack Socket Mode for real-time messaging"""
    console.print("\n[bold green]Testing Slack Socket Mode[/bold green]")
    
    if not os.environ.get('SLACK_BOT_TOKEN') or not os.environ.get('SLACK_APP_TOKEN'):
        console.print("[bold red]Error: SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in environment variables[/bold red]")
        console.print("Please add these to your .env file or export them in your shell.")
        return False
    
    try:
        # Initialize the Slack service
        console.print("\n[bold blue]Initializing Slack service with Socket Mode...[/bold blue]")
        slack_service = SlackService()
        
        # Define a simple callback function
        def echo_message(channel_id, user_id, text, event_data):
            console.print(f"[bold blue]Received message:[/bold blue] {text}")
            console.print(f"[bold blue]From user:[/bold blue] {user_id}")
            console.print(f"[bold blue]In channel:[/bold blue] {channel_id}")
            
            # Echo the message back
            slack_service.send_message(
                channel=channel_id,
                text=f"You said: {text}"
            )
        
        # Start listening for messages
        console.print("\n[bold blue]Starting to listen for messages...[/bold blue]")
        console.print("[italic](Send a message in Slack to see it echoed back)[/italic]")
        console.print("[italic](Press Ctrl+C to exit after testing)[/italic]")
        
        client = slack_service.listen_for_messages(echo_message)
        
        # Keep the test running for a while
        try:
            wait_time = 60  # seconds
            for i in range(wait_time):
                time.sleep(1)
                # Show a progress counter
                if i % 5 == 0:
                    console.print(f"Listening... ({wait_time - i} seconds remaining)")
        except KeyboardInterrupt:
            pass
        
        # Close the connection
        slack_service.close_connection()
        console.print("\n[bold green]Socket Mode test completed![/bold green]")
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        
        if "cannot use socket mode" in str(e).lower() or "invalid_auth" in str(e).lower():
            console.print("\n[bold yellow]Socket Mode Error:[/bold yellow]")
            console.print("1. Make sure your SLACK_APP_TOKEN starts with 'xapp-'")
            console.print("2. Verify Socket Mode is enabled in your Slack app settings")
            console.print("3. Ensure your app is subscribed to the messages.channels event")
        
        return False

if __name__ == "__main__":
    # First test basic functionality
    if test_slack_basic_functionality():
        # If successful, ask if user wants to test Socket Mode
        test_socket = input("\nDo you want to test Socket Mode for real-time messaging? (yes/no): ").strip().lower()
        if test_socket == "yes":
            test_socket_mode()
    
    console.print("\n[bold green]All tests completed![/bold green]") 