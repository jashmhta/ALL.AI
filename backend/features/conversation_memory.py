import os
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
import json

class ConversationMemory:
    """
    Manages conversation history and context for the Multi-AI application.
    Provides methods for storing, retrieving, and managing conversation data.
    """
    
    def __init__(self, max_history_length: int = 20, max_context_tokens: int = 4000):
        """
        Initialize the conversation memory manager.
        
        Args:
            max_history_length: Maximum number of messages to store per conversation
            max_context_tokens: Maximum number of tokens to include in context
        """
        self.conversations = {}
        self.max_history_length = max_history_length
        self.max_context_tokens = max_context_tokens
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "conversations")
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def add_message(self, conversation_id: str, role: str, content: str, model: Optional[str] = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            conversation_id: Unique identifier for the conversation
            role: Role of the message sender (user or assistant)
            content: Content of the message
            model: Model that generated the message (for assistant messages)
        """
        # Initialize conversation if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        # Add the message
        self.conversations[conversation_id].append({
            "role": role,
            "content": content,
            "model": model,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Trim history if it exceeds the maximum length
        if len(self.conversations[conversation_id]) > self.max_history_length:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history_length:]
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get the full conversation history.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of message dictionaries
        """
        return self.conversations.get(conversation_id, [])
    
    def get_context_for_prompt(self, conversation_id: str, max_messages: Optional[int] = None) -> str:
        """
        Get formatted conversation context for inclusion in a prompt.
        
        Args:
            conversation_id: Unique identifier for the conversation
            max_messages: Maximum number of messages to include (defaults to all)
            
        Returns:
            Formatted conversation context string
        """
        history = self.conversations.get(conversation_id, [])
        
        if not history:
            return ""
        
        # Limit the number of messages if specified
        if max_messages is not None:
            history = history[-max_messages:]
        
        # Format the conversation context
        context = "Previous conversation:\n\n"
        
        for message in history:
            role = "User" if message["role"] == "user" else "Assistant"
            model_info = f" ({message['model']})" if message.get("model") else ""
            
            context += f"{role}{model_info}: {message['content']}\n\n"
        
        return context
    
    def clear_conversation(self, conversation_id: str) -> None:
        """
        Clear the conversation history.
        
        Args:
            conversation_id: Unique identifier for the conversation
        """
        if conversation_id in self.conversations:
            self.conversations[conversation_id] = []
    
    def save_conversation(self, conversation_id: str) -> Optional[str]:
        """
        Save the conversation to a file.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Path to the saved file, or None if saving failed
        """
        if conversation_id not in self.conversations or not self.conversations[conversation_id]:
            return None
        
        try:
            # Create a filename with the conversation ID
            filename = f"conversation_{conversation_id}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Prepare the data
            data = {
                "conversation_id": conversation_id,
                "timestamp": asyncio.get_event_loop().time(),
                "messages": self.conversations[conversation_id]
            }
            
            # Write to file
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            
            return filepath
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return None
    
    def load_conversation(self, conversation_id: str) -> bool:
        """
        Load a conversation from a file.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            # Create a filename with the conversation ID
            filename = f"conversation_{conversation_id}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Check if the file exists
            if not os.path.exists(filepath):
                return False
            
            # Read from file
            with open(filepath, "r") as f:
                data = json.load(f)
            
            # Load the conversation
            self.conversations[conversation_id] = data.get("messages", [])
            
            return True
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return False
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Get a list of all saved conversations.
        
        Returns:
            List of conversation metadata dictionaries
        """
        conversations = []
        
        try:
            # List all conversation files
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("conversation_") and filename.endswith(".json"):
                    filepath = os.path.join(self.storage_dir, filename)
                    
                    try:
                        # Read the file
                        with open(filepath, "r") as f:
                            data = json.load(f)
                        
                        # Extract metadata
                        conversation_id = data.get("conversation_id")
                        timestamp = data.get("timestamp")
                        message_count = len(data.get("messages", []))
                        
                        # Add to list
                        conversations.append({
                            "conversation_id": conversation_id,
                            "timestamp": timestamp,
                            "message_count": message_count,
                            "filepath": filepath
                        })
                    except Exception as e:
                        print(f"Error reading conversation file {filename}: {e}")
        except Exception as e:
            print(f"Error listing conversations: {e}")
        
        # Sort by timestamp (newest first)
        conversations.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Remove from memory
            if conversation_id in self.conversations:
                del self.conversations[conversation_id]
            
            # Remove from disk
            filename = f"conversation_{conversation_id}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return True
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for conversations containing the query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching conversation metadata dictionaries
        """
        matching_conversations = []
        
        try:
            # List all conversation files
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("conversation_") and filename.endswith(".json"):
                    filepath = os.path.join(self.storage_dir, filename)
                    
                    try:
                        # Read the file
                        with open(filepath, "r") as f:
                            data = json.load(f)
                        
                        # Check if any message contains the query
                        messages = data.get("messages", [])
                        for message in messages:
                            if query.lower() in message.get("content", "").lower():
                                # Extract metadata
                                conversation_id = data.get("conversation_id")
                                timestamp = data.get("timestamp")
                                message_count = len(messages)
                                
                                # Add to list
                                matching_conversations.append({
                                    "conversation_id": conversation_id,
                                    "timestamp": timestamp,
                                    "message_count": message_count,
                                    "filepath": filepath
                                })
                                
                                # Break to avoid adding the same conversation multiple times
                                break
                    except Exception as e:
                        print(f"Error reading conversation file {filename}: {e}")
        except Exception as e:
            print(f"Error searching conversations: {e}")
        
        # Sort by timestamp (newest first)
        matching_conversations.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        return matching_conversations
