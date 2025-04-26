import sys
import os
import time
import argparse
import logging
from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch
import dotenv
from rich.console import Console
from rich.logging import RichHandler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the necessary modules
from orchestrator.memory.mem0_integration import Mem0Memory
from orchestrator.memory.slack_mem0_adapter import SlackMem0Adapter
from tools.slack.service import SlackService

# Set up logging
FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("rich")

# Create console for pretty output
console = Console()

# Load environment variables
dotenv.load_dotenv()

class TestSlackMem0Integration(unittest.TestCase):
    """Test cases for Slack-Mem0 integration"""
    
    def setUp(self):
        """Set up test environment"""
        # Check if we have the necessary credentials
        self.has_credentials = all([
            os.environ.get('SLACK_BOT_TOKEN'),
            os.environ.get('SLACK_APP_TOKEN'),
            os.environ.get('MEM0_API_KEY')
        ])
        
        if self.has_credentials:
            # Create real instances for integration tests
            self.mem0 = Mem0Memory()
            self.slack_mem0_adapter = SlackMem0Adapter()
        else:
            # Skip tests that require credentials
            log.warning("Skipping integration tests - missing credentials")
        
        # Create a test message
        self.test_message = {
            "channel_id": "C12345",
            "user_id": "U12345",
            "text": "This is a test message for Mem0 integration",
            "event_data": {
                "ts": "1620000000.000000",
                "thread_ts": None
            }
        }
    
    @unittest.skipIf(not os.environ.get('MEM0_API_KEY'), "MEM0_API_KEY not set")
    def test_mem0_add_memory(self):
        """Test adding a memory to Mem0"""
        # Add a test memory
        result = self.mem0.add_memory(
            content="Test memory from integration test",
            metadata={"test": True, "timestamp": datetime.now().isoformat()},
            source="test",
            importance=0.7
        )
        
        # Check that the memory was added successfully
        self.assertIsNotNone(result)
        console.print("[green]✓[/green] Successfully added memory to Mem0")
    
    @unittest.skipIf(not os.environ.get('MEM0_API_KEY'), "MEM0_API_KEY not set")
    def test_mem0_search_memories(self):
        unique_content = f"Unique test content {datetime.now().isoformat()}"
        self.mem0.add_memory(
            content=unique_content,
            metadata={"test": True},
            source="test",
            importance=0.8
        )
        
        # Wait a moment for the memory to be indexed
        time.sleep(1)
        
        # Search for the unique content
        results = self.mem0.search_memories(
            query=unique_content,
            limit=5
        )
        
        # Check that we got results
        self.assertTrue(len(results) > 0)
        console.print(f"[green]✓[/green] Found {len(results)} memories matching the query")
    
    @patch('tools.slack.service.SlackService')
    @patch('orchestrator.mem0_integration.Mem0Memory')
    def test_slack_mem0_adapter_process_message(self, mock_mem0, mock_slack):
        """Test the SlackMem0Adapter's message processing with mocks"""
        # Set up mocks
        mock_mem0_instance = MagicMock()
        mock_mem0.return_value = mock_mem0_instance
        
        mock_slack_instance = MagicMock()
        mock_slack.return_value = mock_slack_instance
        
        # Mock user and channel info
        mock_slack_instance.client.users_info.return_value = {
            "user": {
                "real_name": "Test User",
                "profile": {
                    "email": "test@example.com"
                }
            }
        }
        
        mock_slack_instance.client.conversations_info.return_value = {
            "channel": {
                "name": "test-channel",
                "is_im": False
            }
        }
        
        # Create adapter with mocks
        adapter = SlackMem0Adapter()
        adapter.mem0 = mock_mem0_instance
        adapter.slack = mock_slack_instance
        
        # Process a test message
        adapter._process_message(
            self.test_message["channel_id"],
            self.test_message["user_id"],
            self.test_message["text"],
            self.test_message["event_data"]
        )
        
        # Verify that add_memory was called
        mock_mem0_instance.add_memory.assert_called_once()
        console.print("[green]✓[/green] SlackMem0Adapter successfully processed message")

class SlackMem0Monitor:
    """Listens for Slack messages and stores them in Mem0 for testing"""
    
    def __init__(self):
        """Initialize the monitor"""
        self.adapter = None
    
    def start(self, test_mode=False, duration=60):
        # Check for required environment variables
        required_vars = ['SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN', 'MEM0_API_KEY']
        missing = [var for var in required_vars if not os.environ.get(var)]
        
        if missing:
            console.print("[bold red]Error:[/bold red] Missing required environment variables:")
            for var in missing:
                console.print(f"  - {var}")
            return False
        
        try:
            # Initialize the adapter
            self.adapter = SlackMem0Adapter()
            console.print("[green]✓[/green] Initialized Slack-Mem0 adapter")
            
            if test_mode:
                # In test mode, simulate messages instead of connecting to Slack
                console.print("[bold blue]Running in test mode - simulating messages[/bold blue]")
                self._run_test_simulation(duration)
            else:
                # Start listening for real Slack messages
                console.print("[bold blue]Starting to listen for Slack messages...[/bold blue]")
                console.print("[italic](Press Ctrl+C to stop)[/italic]")
                
                # Start the adapter
                self.adapter.start_listening()
                
                # Keep running until interrupted
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Stopping on user request[/yellow]")
                finally:
                    # Clean up
                    if self.adapter:
                        self.adapter.close()
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
    
    def _run_test_simulation(self, duration):
        """Simulate message processing for testing
        
        Args:
            duration (int): How long to run the simulation (seconds)
        """
        # Create test messages
        test_messages = [
            {
                "channel_id": "C12345",
                "user_id": "U12345",
                "text": "Hello team! Let's discuss the project timeline.",
                "event_data": {"ts": "1620000001.000000", "thread_ts": None}
            },
            {
                "channel_id": "C12345",
                "user_id": "U67890",
                "text": "Sure, I think we need to schedule a meeting with the stakeholders.",
                "event_data": {"ts": "1620000002.000000", "thread_ts": "1620000001.000000"}
            },
            {
                "channel_id": "C12345",
                "user_id": "U12345",
                "text": "Good idea. Can someone create a task for preparing the presentation?",
                "event_data": {"ts": "1620000003.000000", "thread_ts": "1620000001.000000"}
            },
            {
                "channel_id": "C12345",
                "user_id": "U24680",
                "text": "I'll handle that. When do you need it by?",
                "event_data": {"ts": "1620000004.000000", "thread_ts": "1620000001.000000"}
            },
            {
                "channel_id": "C12345",
                "user_id": "U12345",
                "text": "We need it urgently by Friday for the executive review.",
                "event_data": {"ts": "1620000005.000000", "thread_ts": "1620000001.000000"}
            }
        ]
        
        # Mock methods that make API calls
        self.adapter.slack.client.users_info = MagicMock(return_value={
            "user": {
                "real_name": "Test User",
                "profile": {"email": "test@example.com"}
            }
        })
        
        self.adapter.slack.client.conversations_info = MagicMock(return_value={
            "channel": {
                "name": "test-channel",
                "is_im": False
            }
        })
        
        # Process the test messages
        start_time = time.time()
        end_time = start_time + duration
        message_index = 0
        
        console.print(f"[bold blue]Starting test simulation for {duration} seconds...[/bold blue]")
        
        while time.time() < end_time:
            # Process each message with a delay
            msg = test_messages[message_index % len(test_messages)]
            
            console.print(f"[blue]Processing message:[/blue] {msg['text']}")
            
            # Process the message
            self.adapter._process_message(
                msg["channel_id"],
                msg["user_id"],
                msg["text"],
                msg["event_data"]
            )
            
            # Increment index
            message_index += 1
            
            # Add some variety to the test messages
            if message_index % len(test_messages) == 0:
                # Create a new random message
                new_msg = {
                    "channel_id": "C12345",
                    "user_id": f"U{message_index % 100000}",
                    "text": f"Test message {message_index} at {datetime.now().isoformat()}",
                    "event_data": {"ts": f"{time.time()}", "thread_ts": None}
                }
                test_messages.append(new_msg)
            
            # Sleep between messages
            time.sleep(2)
        
        # Store any remaining conversations
        self.adapter.store_all_active_conversations()
        console.print("[green]✓[/green] Test simulation completed")

def main():
    parser = argparse.ArgumentParser(description='Test Slack-Mem0 integration')
    parser.add_argument('--monitor', action='store_true', help='Run as a monitor instead of tests')
    parser.add_argument('--test', action='store_true', help='Run in test mode with simulated messages')
    parser.add_argument('--duration', type=int, default=30, help='Duration for test mode (seconds)')
    args = parser.parse_args()
    
    if args.monitor:
        # Run as a monitor
        monitor = SlackMem0Monitor()
        monitor.start(test_mode=args.test, duration=args.duration)
    else:
        # Run unittest test cases
        unittest.main(argv=[sys.argv[0]])

if __name__ == "__main__":
    main() 