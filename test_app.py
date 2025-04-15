import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from backend.clients.openai_client import OpenAIClient
from backend.clients.claude_client import ClaudeClient
from backend.clients.gemini_client import GeminiClient
from backend.clients.llama_client import LlamaClient
from backend.clients.huggingface_client import HuggingFaceClient
from backend.clients.openrouter_client import OpenRouterClient
from backend.clients.deepseek_client import DeepSeekClient
from backend.clients.synthesis_client import SynthesisClient
from backend.features.conversation_memory import ConversationMemory
from backend.features.file_processor import FileProcessor
from backend.features.credit_tracker import CreditTracker

class TestAIClients(unittest.TestCase):
    """Test cases for AI client implementations."""
    
    def test_openai_client_initialization(self):
        """Test OpenAI client initialization."""
        client = OpenAIClient(api_key="test_key")
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.default_model, "gpt-3.5-turbo")
        self.assertIn("gpt-4", client.get_available_models())
    
    def test_claude_client_initialization(self):
        """Test Claude client initialization."""
        client = ClaudeClient(api_key="test_key")
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.default_model, "claude-3-sonnet")
        self.assertIn("claude-3-opus", client.get_available_models())
    
    def test_gemini_client_initialization(self):
        """Test Gemini client initialization."""
        client = GeminiClient(api_key="test_key")
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.default_model, "gemini-pro")
        self.assertIn("gemini-pro-vision", client.get_available_models())
    
    def test_llama_client_initialization(self):
        """Test Llama client initialization."""
        client = LlamaClient(api_key="test_key")
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.default_model, "llama-3-8b")
        self.assertIn("llama-3-70b", client.get_available_models())
    
    def test_huggingface_client_initialization(self):
        """Test HuggingFace client initialization."""
        client = HuggingFaceClient(api_key="test_key")
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.default_model, "mistral-7b")
        self.assertIn("falcon-40b", client.get_available_models())
    
    def test_openrouter_client_initialization(self):
        """Test OpenRouter client initialization."""
        client = OpenRouterClient(api_key="test_key")
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.default_model, "openai/gpt-4-turbo")
        self.assertIn("anthropic/claude-3-opus", client.get_available_models())
    
    def test_deepseek_client_initialization(self):
        """Test DeepSeek client initialization."""
        client = DeepSeekClient(api_key="test_key")
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.default_model, "deepseek-chat")
        self.assertIn("deepseek-coder", client.get_available_models())
    
    @patch('requests.post')
    def test_openai_query(self, mock_post):
        """Test OpenAI query method."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        # Test query
        client = OpenAIClient(api_key="test_key")
        response = client.query("Test prompt")
        
        # Verify
        self.assertEqual(response, "Test response")
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_claude_query(self, mock_post):
        """Test Claude query method."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "Test response"}]
        }
        mock_post.return_value = mock_response
        
        # Test query
        client = ClaudeClient(api_key="test_key")
        response = client.query("Test prompt")
        
        # Verify
        self.assertEqual(response, "Test response")
        mock_post.assert_called_once()
    
    def test_llama_local_fallback(self):
        """Test Llama local fallback."""
        client = LlamaClient(api_key="test_key")
        response = client._local_fallback("summarize this text")
        self.assertIn("summary", response.lower())
        
        response = client._local_fallback("write code")
        self.assertIn("```python", response)
        
        response = client._local_fallback("explain this concept")
        self.assertIn("explain", response.lower())


class TestSynthesisClient(unittest.TestCase):
    """Test cases for the Synthesis client."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = SynthesisClient()
    
    def test_initialization(self):
        """Test initialization."""
        self.assertIn("parallel", self.client.synthesis_methods)
        self.assertIn("sequential", self.client.synthesis_methods)
        self.assertIn("debate", self.client.synthesis_methods)
        self.assertEqual(self.client.default_method, "parallel")
    
    @patch('asyncio.gather')
    async def test_parallel_synthesis(self, mock_gather):
        """Test parallel synthesis."""
        # Mock models
        model1 = MagicMock()
        model1.query_async = MagicMock(return_value="Response 1")
        model2 = MagicMock()
        model2.query_async = MagicMock(return_value="Response 2")
        
        models = [
            {"name": "Model1", "client": model1},
            {"name": "Model2", "client": model2}
        ]
        
        # Mock gather results
        mock_gather.return_value = [
            {"model": "Model1", "response": "Response 1"},
            {"model": "Model2", "response": "Response 2"}
        ]
        
        # Test synthesis
        result = await self.client._parallel_synthesis(
            prompt="Test prompt",
            models=models,
            llama_client=None
        )
        
        # Verify
        self.assertIn("individual_responses", result)
        self.assertIn("synthesized_response", result)
        self.assertEqual(result["method"], "parallel")
    
    def test_simple_synthesis(self):
        """Test simple synthesis."""
        responses = [
            {"model": "Model1", "response": "Response 1"},
            {"model": "Model2", "response": "Response 2"}
        ]
        
        result = self.client._simple_synthesis(responses)
        
        self.assertIn("Model1", result)
        self.assertIn("Response 1", result)
        self.assertIn("Model2", result)
        self.assertIn("Response 2", result)


class TestConversationMemory(unittest.TestCase):
    """Test cases for the Conversation Memory."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory = ConversationMemory()
    
    def test_add_message(self):
        """Test adding messages."""
        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi there")
        
        history = self.memory.get_conversation_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hi there")
    
    def test_clear_conversation(self):
        """Test clearing conversation."""
        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi there")
        
        self.memory.clear_conversation()
        history = self.memory.get_conversation_history()
        self.assertEqual(len(history), 0)
    
    def test_get_context_window(self):
        """Test getting context window."""
        self.memory.add_message("user", "Message 1")
        self.memory.add_message("assistant", "Response 1")
        self.memory.add_message("user", "Message 2")
        self.memory.add_message("assistant", "Response 2")
        
        context = self.memory.get_context_window(max_tokens=100)
        self.assertEqual(len(context), 4)
        
        # Test with token limit
        self.memory.add_message("user", "A" * 1000)  # Long message
        context = self.memory.get_context_window(max_tokens=100)
        self.assertLess(len(context), 5)  # Should truncate


class TestFileProcessor(unittest.TestCase):
    """Test cases for the File Processor."""
    
    def setUp(self):
        """Set up test environment."""
        self.processor = FileProcessor()
    
    def test_get_file_extension(self):
        """Test getting file extension."""
        self.assertEqual(self.processor.get_file_extension("test.txt"), ".txt")
        self.assertEqual(self.processor.get_file_extension("test.pdf"), ".pdf")
        self.assertEqual(self.processor.get_file_extension("test"), "")
    
    def test_get_mime_type(self):
        """Test getting MIME type."""
        self.assertEqual(self.processor.get_mime_type("test.txt"), "text/plain")
        self.assertEqual(self.processor.get_mime_type("test.pdf"), "application/pdf")
        self.assertEqual(self.processor.get_mime_type("test.jpg"), "image/jpeg")
    
    def test_is_supported_file_type(self):
        """Test checking supported file types."""
        self.assertTrue(self.processor.is_supported_file_type("test.txt"))
        self.assertTrue(self.processor.is_supported_file_type("test.pdf"))
        self.assertTrue(self.processor.is_supported_file_type("test.jpg"))
        self.assertFalse(self.processor.is_supported_file_type("test.unsupported"))


class TestCreditTracker(unittest.TestCase):
    """Test cases for the Credit Tracker."""
    
    def setUp(self):
        """Set up test environment."""
        # Use in-memory storage for testing
        self.tracker = CreditTracker(storage_path=":memory:")
    
    def test_initialization(self):
        """Test initialization."""
        self.assertIn("openai", self.tracker.credits_data["providers"])
        self.assertIn("claude", self.tracker.credits_data["providers"])
        self.assertIn("gemini", self.tracker.credits_data["providers"])
        self.assertIn("llama", self.tracker.credits_data["providers"])
        self.assertIn("huggingface", self.tracker.credits_data["providers"])
        self.assertIn("openrouter", self.tracker.credits_data["providers"])
        self.assertIn("deepseek", self.tracker.credits_data["providers"])
    
    def test_get_remaining_credits(self):
        """Test getting remaining credits."""
        # Initial credits should be 10.0
        self.assertEqual(self.tracker.get_remaining_credits("openai"), 10.0)
        
        # Track some usage
        self.tracker.track_usage("openai", "gpt-4", 100, 50)
        
        # Should be less than 10.0 now
        self.assertLess(self.tracker.get_remaining_credits("openai"), 10.0)
    
    def test_track_usage(self):
        """Test tracking usage."""
        usage = self.tracker.track_usage("claude", "claude-3-opus", 200, 100)
        
        self.assertEqual(usage["provider"], "claude")
        self.assertEqual(usage["model"], "claude-3-opus")
        self.assertEqual(usage["input_tokens"], 200)
        self.assertEqual(usage["output_tokens"], 100)
        self.assertGreater(usage["cost"], 0)
    
    def test_add_credits(self):
        """Test adding credits."""
        initial = self.tracker.get_remaining_credits("gemini")
        self.tracker.add_credits("gemini", 5.0)
        after = self.tracker.get_remaining_credits("gemini")
        
        self.assertEqual(after, initial + 5.0)
    
    def test_reset_credits(self):
        """Test resetting credits."""
        # Track some usage
        self.tracker.track_usage("llama", "llama-3-70b", 300, 150)
        
        # Verify credits used
        self.assertLess(self.tracker.get_remaining_credits("llama"), 10.0)
        
        # Reset
        self.tracker.reset_credits("llama")
        
        # Should be back to 10.0
        self.assertEqual(self.tracker.get_remaining_credits("llama"), 10.0)
    
    def test_get_usage_summary(self):
        """Test getting usage summary."""
        # Track some usage
        self.tracker.track_usage("openai", "gpt-4", 100, 50)
        self.tracker.track_usage("openai", "gpt-3.5-turbo", 200, 100)
        self.tracker.track_usage("claude", "claude-3-opus", 300, 150)
        
        # Get summary
        summary = self.tracker.get_usage_summary()
        
        self.assertEqual(summary["request_count"], 3)
        self.assertEqual(summary["total_input_tokens"], 600)
        self.assertEqual(summary["total_output_tokens"], 300)
        self.assertGreater(summary["total_cost"], 0)
        self.assertIn("openai", summary["providers"])
        self.assertIn("claude", summary["providers"])
        self.assertIn("gpt-4", summary["models"])
        self.assertIn("gpt-3.5-turbo", summary["models"])
        self.assertIn("claude-3-opus", summary["models"])


if __name__ == "__main__":
    unittest.main()
