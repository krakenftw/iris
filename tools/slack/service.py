import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
import logging
import re
from datetime import datetime

class SlackService:
    def __init__(self, bot_token=None, app_token=None):
        """Initialize Slack service with API tokens
        
        Args:
            bot_token (str, optional): Slack bot token. If not provided, will look for SLACK_BOT_TOKEN env variable
            app_token (str, optional): Slack app token for Socket Mode. If not provided, will look for SLACK_APP_TOKEN env variable
        """
        self.bot_token = bot_token or os.environ.get('SLACK_BOT_TOKEN')
        self.app_token = app_token or os.environ.get('SLACK_APP_TOKEN')
        
        if not self.bot_token:
            raise ValueError("Slack bot token must be provided or set in SLACK_BOT_TOKEN environment variable")
            
        # Initialize regular Web API client
        self.client = WebClient(token=self.bot_token)
        self.socket_client = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # If app token is provided, initialize Socket Mode client for real-time messaging
        if self.app_token:
            if not self.app_token.startswith("xapp-"):
                raise ValueError("Slack app token must start with 'xapp-'")
            self.socket_client = SocketModeClient(
                app_token=self.app_token,
                web_client=self.client
            )
    
    def send_message(self, channel, text, blocks=None, thread_ts=None):
        """Send a message to a Slack channel
        
        Args:
            channel (str): Channel ID or name
            text (str): Message text
            blocks (list, optional): Block Kit blocks for rich formatting
            thread_ts (str, optional): Thread timestamp to reply in a thread
            
        Returns:
            dict: Response from Slack API
        """
        try:
            return self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks,
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            self.logger.error(f"Error sending message: {e}")
            raise
    
    def send_direct_message(self, user_id, text, blocks=None):
        """Send a direct message to a user
        
        Args:
            user_id (str): User ID
            text (str): Message text
            blocks (list, optional): Block Kit blocks for rich formatting
            
        Returns:
            dict: Response from Slack API
        """
        try:
            # Open a DM channel with the user
            response = self.client.conversations_open(users=user_id)
            channel_id = response['channel']['id']
            
            # Send message to the DM channel
            return self.client.chat_postMessage(
                channel=channel_id,
                text=text,
                blocks=blocks
            )
        except SlackApiError as e:
            self.logger.error(f"Error sending direct message: {e}")
            raise
    
    def get_user_by_email(self, email):
        """Get user info by email address
        
        Args:
            email (str): User's email address
            
        Returns:
            dict: User information
        """
        try:
            response = self.client.users_lookupByEmail(email=email)
            return response['user']
        except SlackApiError as e:
            self.logger.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_name(self, username):
        """Find a user by their display name
        
        Args:
            username (str): User's display name or real name
            
        Returns:
            dict: User information or None if not found
        """
        try:
            # Get all users
            response = self.client.users_list()
            users = response['members']
            
            # Search for user by display name or real name
            username = username.lower()
            for user in users:
                if (
                    user.get('profile', {}).get('display_name', '').lower() == username or
                    user.get('profile', {}).get('real_name', '').lower() == username
                ):
                    return user
            
            return None
        except SlackApiError as e:
            self.logger.error(f"Error getting user by name: {e}")
            return None
    
    def listen_for_messages(self, callback_function):
        """Listen for messages in real-time using Socket Mode
        
        Args:
            callback_function: Function to call when a message is received
                The function should accept (channel_id, user_id, text, event_data)
        
        Note: Requires app_token to be set and proper permissions
        """
        if not self.socket_client:
            raise ValueError("Socket Mode client not initialized. Make sure SLACK_APP_TOKEN is set.")
        
        def process_event(client: SocketModeClient, req: SocketModeRequest):
            if req.type == "events_api":
                # Extract the event from the payload
                event_data = req.payload.get("event", {})
                
                # Acknowledge the request
                client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
                
                # Only process message events that are not from bots
                if (
                    event_data.get("type") == "message" and
                    event_data.get("subtype") not in ["bot_message", "message_changed", "message_deleted"]
                ):
                    channel_id = event_data.get("channel")
                    user_id = event_data.get("user")
                    text = event_data.get("text", "")
                    
                    # Call the provided callback function with the message details
                    callback_function(channel_id, user_id, text, event_data)
        
        # Register the event listener
        self.socket_client.socket_mode_request_listeners.append(process_event)
        self.logger.info("Starting to listen for Slack messages...")
        
        # Start the client
        self.socket_client.connect()
        
        return self.socket_client
    
    def format_task_message(self, task_info):
        """Format a message about a task using Block Kit
        
        Args:
            task_info (dict): Task information including title, description, assignee, etc.
            
        Returns:
            list: Block Kit blocks
        """
        # Create formatted timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 New Task Created: {task_info.get('title', 'Untitled')}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Assignee:*\n{task_info.get('assignee', 'Unassigned')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{task_info.get('priority', 'Normal')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{task_info.get('description', 'No description')}"
                }
            }
        ]
        
        # Add URL if available
        if task_info.get('url'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{task_info['url']}|View in Linear>"
                }
            })
        
        # Add meeting info if available
        if task_info.get('meeting'):
            meeting_time = task_info['meeting'].get('time', 'Not specified')
            meeting_link = task_info['meeting'].get('link', '')
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Meeting scheduled:*\n{meeting_time}"
                }
            })
            
            if meeting_link:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<{meeting_link}|Join Meeting>"
                    }
                })
        
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Created at {timestamp}",
                    "emoji": True
                }
            ]
        })
        
        return blocks
    
    def extract_mentions(self, text):
        """Extract user mentions from a message
        
        Args:
            text (str): Message text
            
        Returns:
            list: List of user IDs mentioned
        """
        mention_pattern = r"<@(U[A-Z0-9]+)>"
        return re.findall(mention_pattern, text)
    
    def close_connection(self):
        """Close the Socket Mode connection if open"""
        if self.socket_client:
            self.socket_client.close()
            self.logger.info("Closed Slack connection") 