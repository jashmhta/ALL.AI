import os
import json
from typing import Dict, Any, List, Optional

class ConversationMemory:
    """
    Manages conversation history and context for multi-turn conversations.
    Provides context window management and conversation persistence.
    """
    
    def __init__(self, max_history: int = 10, context_window: int = 4000):
        """
        Initialize the conversation memory.
        
        Args:
            max_history: Maximum number of conversation turns to store
            context_window: Maximum number of tokens to include in context
        """
        self.max_history = max_history
        self.context_window = context_window
        self.conversations = {}
        
        # Create directory for storing conversations
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "conversations")
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def add_message(self, conversation_id: str, role: str, content: str, model: str = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            conversation_id: Unique identifier for the conversation
            role: Role of the message sender (user or assistant)
            content: Message content
            model: AI model that generated the message (for assistant messages)
        """
        # Initialize conversation if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        # Add message to history
        message = {
            "role": role,
            "content": content
        }
        
        # Add model information for assistant messages
        if role == "assistant" and model:
            message["model"] = model
        
        self.conversations[conversation_id].append(message)
        
        # Trim history if it exceeds max_history
        if len(self.conversations[conversation_id]) > self.max_history * 2:  # *2 because each turn has user+assistant
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history*2:]
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get the full conversation history.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of messages in the conversation
        """
        return self.conversations.get(conversation_id, [])
    
    def get_context_for_prompt(self, conversation_id: str, include_last_n: int = None) -> str:
        """
        Get formatted conversation history for including in prompts.
        
        Args:
            conversation_id: Unique identifier for the conversation
            include_last_n: Number of most recent turns to include (None for all)
            
        Returns:
            Formatted conversation history
        """
        history = self.conversations.get(conversation_id, [])
        
        if not history:
            return ""
        
        # Limit to last N turns if specified
        if include_last_n is not None:
            history = history[-include_last_n*2:]  # *2 because each turn has user+assistant
        
        # Format conversation history
        formatted_history = "Previous conversation:\n\n"
        
        for message in history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                formatted_history += f"User: {content}\n\n"
            elif role == "assistant":
                model = message.get("model", "AI")
                formatted_history += f"Assistant ({model}): {content}\n\n"
        
        return formatted_history
    
    def get_messages_for_model(self, conversation_id: str, include_last_n: int = None) -> List[Dict[str, str]]:
        """
        Get messages formatted for API calls to models like OpenAI.
        
        Args:
            conversation_id: Unique identifier for the conversation
            include_last_n: Number of most recent turns to include (None for all)
            
        Returns:
            List of messages in the format expected by OpenAI and similar APIs
        """
        history = self.conversations.get(conversation_id, [])
        
        if not history:
            return []
        
        # Limit to last N turns if specified
        if include_last_n is not None:
            history = history[-include_last_n*2:]  # *2 because each turn has user+assistant
        
        # Format for API calls
        formatted_messages = []
        
        for message in history:
            formatted_message = {
                "role": message["role"],
                "content": message["content"]
            }
            formatted_messages.append(formatted_message)
        
        return formatted_messages
    
    def save_conversation(self, conversation_id: str) -> str:
        """
        Save a conversation to disk.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Path to the saved conversation file
        """
        if conversation_id not in self.conversations:
            return None
        
        # Create filename
        filename = f"conversation_{conversation_id}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        # Save conversation to file
        with open(filepath, 'w') as f:
            json.dump(self.conversations[conversation_id], f, indent=2)
        
        return filepath
    
    def load_conversation(self, conversation_id: str) -> bool:
        """
        Load a conversation from disk.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if the conversation was loaded successfully, False otherwise
        """
        # Create filename
        filename = f"conversation_{conversation_id}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return False
        
        # Load conversation from file
        try:
            with open(filepath, 'r') as f:
                self.conversations[conversation_id] = json.load(f)
            return True
        except Exception:
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation from memory and disk.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if the conversation was deleted successfully, False otherwise
        """
        # Remove from memory
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
        
        # Remove from disk
        filename = f"conversation_{conversation_id}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception:
                return False
        
        return True
    
    def list_saved_conversations(self) -> List[str]:
        """
        List all saved conversations.
        
        Returns:
            List of conversation IDs
        """
        conversations = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.startswith("conversation_") and filename.endswith(".json"):
                conversation_id = filename[13:-5]  # Remove "conversation_" prefix and ".json" suffix
                conversations.append(conversation_id)
        
        return conversations
    
    def estimate_token_count(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        This is a simple approximation, not exact.
        
        Args:
            text: Text to estimate token count for
            
        Returns:
            Estimated number of tokens
        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def trim_context_to_fit(self, context: str, max_tokens: int = None) -> str:
        """
        Trim context to fit within token limit.
        
        Args:
            context: Context to trim
            max_tokens: Maximum number of tokens (defaults to self.context_window)
            
        Returns:
            Trimmed context
        """
        max_tokens = max_tokens or self.context_window
        
        # If context is already within limit, return as is
        if self.estimate_token_count(context) <= max_tokens:
            return context
        
        # Split into lines
        lines = context.split('\n\n')
        
        # Keep most recent lines that fit within token limit
        trimmed_context = ""
        for line in reversed(lines):
            new_context = line + '\n\n' + trimmed_context
            if self.estimate_token_count(new_context) > max_tokens:
                break
            trimmed_context = new_context
        
        # Add note about trimmed context
        if trimmed_context != context:
            trimmed_context = "[Note: Some earlier messages have been omitted to fit within context limits]\n\n" + trimmed_context
        
        return trimmed_context.strip()
