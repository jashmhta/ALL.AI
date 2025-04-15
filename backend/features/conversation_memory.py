import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class ConversationMemory:
    """
    Manages conversation history and context for AI interactions.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the conversation memory.
        
        Args:
            storage_path: Optional path to store conversation history
        """
        self.storage_path = storage_path
        self.conversation_history = []
        self.max_history_length = 100  # Default max history length
        
        # Load existing conversation if storage path is provided
        if storage_path and os.path.exists(storage_path):
            self._load_conversation()
    
    def add_message(self, role: str, content: str) -> Dict[str, Any]:
        """
        Add a message to the conversation history.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            
        Returns:
            Added message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history.append(message)
        
        # Trim history if it exceeds max length
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
        
        # Save conversation if storage path is provided
        if self.storage_path:
            self._save_conversation()
        
        return message
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the full conversation history.
        
        Returns:
            List of messages
        """
        return self.conversation_history
    
    def clear_conversation(self) -> None:
        """
        Clear the conversation history.
        """
        self.conversation_history = []
        
        # Save empty conversation if storage path is provided
        if self.storage_path:
            self._save_conversation()
    
    def get_context_window(self, max_tokens: int = 4000) -> List[Dict[str, str]]:
        """
        Get a context window of messages that fits within token limit.
        
        Args:
            max_tokens: Maximum tokens in context window
            
        Returns:
            List of messages for context window
        """
        # Simple token estimation (4 chars ≈ 1 token)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4
        
        # Start with most recent messages
        context = []
        token_count = 0
        
        # Add messages from newest to oldest until token limit is reached
        for message in reversed(self.conversation_history):
            message_tokens = estimate_tokens(message["content"])
            
            if token_count + message_tokens <= max_tokens:
                # Add message to context (at the beginning to maintain order)
                context.insert(0, {
                    "role": message["role"],
                    "content": message["content"]
                })
                token_count += message_tokens
            else:
                # Token limit reached
                break
        
        return context
    
    def summarize_conversation(self, max_length: int = 200) -> str:
        """
        Generate a summary of the conversation.
        
        Args:
            max_length: Maximum length of summary in characters
            
        Returns:
            Conversation summary
        """
        if not self.conversation_history:
            return "No conversation history."
        
        # Count messages by role
        user_messages = sum(1 for m in self.conversation_history if m["role"] == "user")
        assistant_messages = sum(1 for m in self.conversation_history if m["role"] == "assistant")
        
        # Get first and last messages
        first_message = self.conversation_history[0]
        last_message = self.conversation_history[-1]
        
        # Create summary
        summary = f"Conversation with {user_messages} user messages and {assistant_messages} assistant responses. "
        
        # Add first user message
        first_user_message = next((m for m in self.conversation_history if m["role"] == "user"), None)
        if first_user_message:
            first_content = first_user_message["content"]
            if len(first_content) > 50:
                first_content = first_content[:47] + "..."
            summary += f"Started with: \"{first_content}\" "
        
        # Add last exchange
        last_user_message = next((m for m in reversed(self.conversation_history) if m["role"] == "user"), None)
        if last_user_message:
            last_content = last_user_message["content"]
            if len(last_content) > 50:
                last_content = last_content[:47] + "..."
            summary += f"Latest user query: \"{last_content}\""
        
        # Truncate if necessary
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
    
    def _save_conversation(self) -> None:
        """
        Save conversation history to storage.
        """
        try:
            with open(self.storage_path, 'w') as f:
                json.dump({
                    "history": self.conversation_history,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving conversation: {str(e)}")
    
    def _load_conversation(self) -> None:
        """
        Load conversation history from storage.
        """
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.conversation_history = data.get("history", [])
        except Exception as e:
            print(f"Error loading conversation: {str(e)}")
            self.conversation_history = []
    
    def get_last_n_messages(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get the last N messages from conversation history.
        
        Args:
            n: Number of messages to retrieve
            
        Returns:
            List of last N messages
        """
        return self.conversation_history[-n:] if self.conversation_history else []
    
    def get_messages_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        Get all messages with a specific role.
        
        Args:
            role: Role to filter by (user, assistant, system)
            
        Returns:
            List of messages with specified role
        """
        return [m for m in self.conversation_history if m["role"] == role]
    
    def set_max_history_length(self, length: int) -> None:
        """
        Set maximum history length.
        
        Args:
            length: Maximum number of messages to keep
        """
        self.max_history_length = max(10, length)  # Minimum of 10 messages
        
        # Trim history if it exceeds new max length
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
