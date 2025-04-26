import os
import logging
from mem0 import MemoryClient

class Mem0Memory:
    """Memory integration using Mem0's API"""
    
    def __init__(self, api_key=None):
        """Initialize Mem0 memory integration
        
        Args:
            api_key (str, optional): Mem0 API key. If not provided, looks for MEM0_API_KEY in env variables
        """
        self.api_key = api_key or os.environ.get('MEM0_API_KEY')
        if not self.api_key:
            raise ValueError("Mem0 API key must be provided or set in MEM0_API_KEY environment variable")
        
        self.logger = logging.getLogger(__name__)
        self.client = MemoryClient(api_key=self.api_key)
    
    def add_memory(self, content, metadata=None, user_id=None,agent_id=None):
        meta = metadata or {}
            
        print(f"Adding memory: {content}, {meta}, {user_id}, {agent_id}")
        
        try:
            self.client.add(messages=content, user_id=user_id, agent_id=agent_id, metadata=meta)
        except Exception as e:
            self.logger.error(f"Error adding memory to Mem0: {str(e)}")
            return None
    
    def search_memories(self, query, user_id=None, metadata_filter=None):
        try:
            return self.client.search(query, user_id=user_id, metadata=metadata_filter)
        except Exception as e:
            self.logger.error(f"Error searching memories in Mem0: {str(e)}")
            return []