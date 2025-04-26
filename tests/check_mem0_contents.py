import sys
import os
import argparse
import json
from datetime import datetime, timedelta
import dotenv
from rich.console import Console
from rich.table import Table
from rich.text import Text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Mem0 integration
from orchestrator.mem0_integration import Mem0Memory

# Create console for pretty output
console = Console()

# Load environment variables
dotenv.load_dotenv()

def check_mem0_contents(query=None, source=None, limit=10):
    """Check the contents of Mem0 and display them
    
    Args:
        query (str, optional): Search query to filter memories
        source (str, optional): Source to filter memories (slack, linear, etc.)
        limit (int, optional): Maximum number of memories to retrieve
    """
    # Check if Mem0 API key is set
    if not os.environ.get('MEM0_API_KEY'):
        console.print("[bold red]Error:[/bold red] MEM0_API_KEY environment variable not set")
        return False
    
    try:
        # Initialize Mem0 memory
        mem0 = Mem0Memory()
        
        # Prepare metadata filter if source is specified
        metadata_filter = None
        if source:
            metadata_filter = {"source": source}
        
        # Search for memories
        console.print(f"[bold blue]Searching Mem0 for memories{' matching: ' + query if query else ''}...[/bold blue]")
        
        memories = mem0.search_memories(
            query=query or "",
            limit=limit,
            metadata_filter=metadata_filter
        )
        
        if not memories:
            console.print("[yellow]No memories found.[/yellow]")
            return True
        
        # Display results in a table
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID", style="dim", width=10)
        table.add_column("Content", width=40)
        table.add_column("Source", width=10)
        table.add_column("Importance", width=10)
        table.add_column("Metadata", width=30)
        
        for memory in memories:
            # Format content for display (truncate if too long)
            content = memory.get('content', '')
            if len(content) > 100:
                content = content[:97] + "..."
            
            # Format metadata for display
            metadata = memory.get('metadata', {})
            metadata_str = json.dumps(metadata, indent=2)
            if len(metadata_str) > 100:
                metadata_str = metadata_str[:97] + "..."
            
            # Format importance
            importance = memory.get('importance', 0)
            importance_str = f"{importance:.2f}"
            
            # Get source from metadata
            source = metadata.get('source', 'unknown')
            
            # Add row to table
            table.add_row(
                str(memory.get('id', '')),
                content,
                source,
                importance_str,
                metadata_str
            )
        
        console.print(f"[green]Found {len(memories)} memories:[/green]")
        console.print(table)
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return False

def analyze_slack_conversations(limit=5):
    """Analyze and display Slack conversations stored in Mem0
    
    Args:
        limit (int, optional): Maximum number of conversations to retrieve
    """
    # Check if Mem0 API key is set
    if not os.environ.get('MEM0_API_KEY'):
        console.print("[bold red]Error:[/bold red] MEM0_API_KEY environment variable not set")
        return False
    
    try:
        # Initialize Mem0 memory
        mem0 = Mem0Memory()
        
        # Search for conversation memories
        metadata_filter = {
            "source": "slack",
            "type": "conversation"
        }
        
        console.print("[bold blue]Searching for Slack conversations in Mem0...[/bold blue]")
        
        memories = mem0.search_memories(
            query="conversation",
            limit=limit,
            metadata_filter=metadata_filter
        )
        
        if not memories:
            console.print("[yellow]No conversations found.[/yellow]")
            return True
        
        # Display results
        console.print(f"[green]Found {len(memories)} conversations:[/green]")
        
        for i, memory in enumerate(memories):
            content = memory.get('content', '')
            participants = memory.get('metadata', {}).get('participants', [])
            
            console.print(f"\n[bold blue]Conversation {i+1}:[/bold blue]")
            
            if participants:
                console.print(f"[bold]Participants:[/bold] {', '.join(participants)}")
            
            # Format the conversation content for display
            lines = content.split('\n')
            for line in lines:
                # Highlight timestamps and usernames
                if line.strip() and '[' in line and ']:' in line:
                    parts = line.split(']:', 1)
                    if len(parts) == 2:
                        timestamp_user = parts[0] + ']'
                        message = parts[1]
                        
                        highlighted = Text(timestamp_user, style="bold cyan")
                        highlighted.append(":" + message)
                        
                        console.print(highlighted)
                else:
                    console.print(line)
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return False

def analyze_tasks(limit=10):
    """Analyze and display tasks stored in Mem0
    
    Args:
        limit (int, optional): Maximum number of tasks to retrieve
    """
    # Check if Mem0 API key is set
    if not os.environ.get('MEM0_API_KEY'):
        console.print("[bold red]Error:[/bold red] MEM0_API_KEY environment variable not set")
        return False
    
    try:
        # Initialize Mem0 memory
        mem0 = Mem0Memory()
        
        # Search for task memories
        metadata_filter = {
            "type": "task"
        }
        
        console.print("[bold blue]Searching for tasks in Mem0...[/bold blue]")
        
        memories = mem0.search_memories(
            query="task",
            limit=limit,
            metadata_filter=metadata_filter
        )
        
        if not memories:
            console.print("[yellow]No tasks found.[/yellow]")
            return True
        
        # Display results in a table
        table = Table(show_header=True, header_style="bold")
        table.add_column("Title", width=30)
        table.add_column("Assignee", width=15)
        table.add_column("Status", width=10)
        table.add_column("Priority", width=10)
        table.add_column("Due Date", width=15)
        
        for memory in enumerate(memories):
            metadata = memory.get('metadata', {})
            
            # Extract task information
            title = metadata.get('title', 'Unknown task')
            assignee = metadata.get('assignee', 'Unassigned')
            status = metadata.get('status', 'Unknown')
            priority = metadata.get('priority', 'Normal')
            due_date = metadata.get('due_date', 'Not set')
            
            # Add row to table
            table.add_row(
                title,
                assignee,
                status,
                priority,
                due_date
            )
        
        console.print(f"[green]Found {len(memories)} tasks:[/green]")
        console.print(table)
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return False

def main():
    """Main function to run the Mem0 content checker"""
    parser = argparse.ArgumentParser(description='Check contents of Mem0')
    parser.add_argument('--query', '-q', type=str, help='Search query for memories')
    parser.add_argument('--source', '-s', type=str, help='Filter by source (slack, linear, etc.)')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Maximum number of memories to retrieve')
    parser.add_argument('--conversations', '-c', action='store_true', help='Display Slack conversations')
    parser.add_argument('--tasks', '-t', action='store_true', help='Display tasks')
    args = parser.parse_args()
    
    # Check if any action is specified
    if args.conversations:
        analyze_slack_conversations(limit=args.limit)
    elif args.tasks:
        analyze_tasks(limit=args.limit)
    else:
        check_mem0_contents(query=args.query, source=args.source, limit=args.limit)

if __name__ == "__main__":
    main() 