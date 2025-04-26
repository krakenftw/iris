from tools.slack.service import SlackService
from orchestrator.mem0_integration import Mem0Memory
import logging
import re

class SlackMem0Adapter:
    def __init__(self, mem0_api_key=None, slack_bot_token=None, slack_app_token=None):
        self.logger = logging.getLogger(__name__)
        self.mem0 = Mem0Memory(api_key=mem0_api_key)
        self.slack = SlackService(bot_token=slack_bot_token, app_token=slack_app_token)
        
        self.active_conversations = {}
    
    def start_listening(self):
        self.logger.info("Starting to listen for Slack messages...")
        return self.slack.listen_for_messages(self._process_message)
    
    def _process_message(self, channel_id, user_id, text, event_data):
        try:
            user_info = self.slack.client.users_info(user=user_id)
            user_name = user_info['user']['real_name']
            user_email = user_info['user'].get('profile', {}).get('email')
        except Exception as e:
            self.logger.error(f"Error getting user info: {str(e)}")
            user_name = user_id
            user_email = None
        
        try:
            channel_info = self.slack.client.conversations_info(channel=channel_id)
            channel_name = channel_info['channel'].get('name', channel_id)
            is_direct_message = channel_info['channel']['is_im']
        except Exception as e:
            self.logger.error(f"Error getting channel info: {str(e)}")
            channel_name = channel_id
            is_direct_message = False
        
        # Calculate importance
        importance = self._calculate_importance(text, is_direct_message, event_data)
        
        # Prepare metadata
        metadata = {
            "source": "slack",
            "channel_id": channel_id,
            "channel_name": channel_name,
            "user_name": user_name,
            "is_direct_message": is_direct_message,
            "ts": event_data.get('ts'),
            "importance": importance,
            "thread_ts": event_data.get('thread_ts')
        }
        
        if user_email:
            metadata["user_email"] = user_email
        
        # Store the message in Mem0
        self.mem0.add_memory(
            content=text,
            metadata=metadata,
            user_id=user_id
        )
        
        # Handle conversation tracking
        self._track_conversation(channel_id, user_id, text, event_data, metadata)
        
    def _calculate_importance(self, text, is_direct_message, event_data):
        """Calculate importance score for a message
        
        Args:
            text (str): Message text
            is_direct_message (bool): Whether this is a DM
            event_data (dict): Full event data
            
        Returns:
            float: Importance score between 0 and 1
        """
        importance = 0.5  # Default importance
        
        # DMs are generally more important
        if is_direct_message:
            importance += 0.2
        
        # Messages in threads might be part of important discussions
        if event_data.get('thread_ts'):
            importance += 0.1
        
        # Keywords that might indicate important content
        important_keywords = [
            "urgent", "important", "priority", "deadline", "alert",
            "attention", "critical", "asap", "help", "issue", "problem",
            "task", "meeting", "schedule", "project", "decision"
        ]
        
        # Check for important keywords
        if any(keyword in text.lower() for keyword in important_keywords):
            importance += 0.2
        
        # Check for mentions
        mentions = re.findall(r"<@([A-Z0-9]+)>", text)
        if mentions:
            importance += 0.1
        
        # Longer messages might contain more valuable information
        if len(text) > 200:
            importance += 0.1
        
        # Ensure importance is between 0 and 1
        return min(max(importance, 0), 1)
    
    def _track_conversation(self, channel_id, user_id, text, event_data, metadata):
        """Track conversations to store them as cohesive units
        
        Args:
            channel_id (str): Channel ID
            user_id (str): User ID
            text (str): Message text
            event_data (dict): Full event data
            metadata (dict): Message metadata
        """
        # Handle thread conversations
        thread_ts = event_data.get('thread_ts') or event_data.get('ts')
        
        # Create conversation ID combining channel and thread
        conversation_key = f"{channel_id}:{thread_ts}"
        
        # Check if this is part of an existing conversation
        if conversation_key not in self.active_conversations:
            # Start a new conversation
            self.active_conversations[conversation_key] = {
                "messages": [],
                "participants": set(),
                "start_time": metadata.get('ts'),
                "channel_name": metadata.get('channel_name'),
                "last_update": metadata.get('ts')
            }
        
        # Add message to conversation
        self.active_conversations[conversation_key]["messages"].append({
            "user_id": user_id,
            "content": text,
            "timestamp": metadata.get('ts'),
            "metadata": metadata
        })
        
        # Add participant
        self.active_conversations[conversation_key]["participants"].add(user_id)
        
        # Update last activity
        self.active_conversations[conversation_key]["last_update"] = metadata.get('ts')
        
        # If conversation has enough messages or enough time has passed,
        # store it as a complete conversation in Mem0
        if len(self.active_conversations[conversation_key]["messages"]) >= 5:
            self._store_conversation(conversation_key)
    
    def _store_conversation(self, conversation_key):
        """Store a completed conversation in Mem0
        
        Args:
            conversation_key (str): Key identifying the conversation
        """
        conversation = self.active_conversations.get(conversation_key)
        if not conversation:
            return
        
        # Create a title for the conversation
        channel_name = conversation.get("channel_name", "Unknown channel")
        first_message = conversation["messages"][0]["content"] if conversation["messages"] else ""
        
        # Format conversation for storage
        conversation_messages = []
        for msg in conversation["messages"]:
            conversation_messages.append({
                "role": "user", 
                "content": msg["content"],
                "user_id": msg["user_id"],
                "timestamp": msg["timestamp"]
            })
            
        # Store the conversation with additional metadata
        conversation_metadata = {
            "source": "slack",
            "type": "conversation",
            "channel_name": channel_name,
            "participants": list(conversation["participants"]),
            "start_time": conversation["start_time"],
            "end_time": conversation["last_update"]
        }
        
        # Store the conversation
        self.mem0.add_memory(
            content=conversation_messages,
            metadata=conversation_metadata,
            user_id=conversation["messages"][0]["user_id"]
        )
        
        # Remove from active conversations
        del self.active_conversations[conversation_key]
    
    def store_all_active_conversations(self):
        """Store all currently active conversations
        This should be called before shutting down the adapter
        """
        for conversation_key in list(self.active_conversations.keys()):
            self._store_conversation(conversation_key)
    
    def close(self):
        """Close connections and clean up"""
        self.store_all_active_conversations()
        if hasattr(self.slack, 'close_connection'):
            self.slack.close_connection() 