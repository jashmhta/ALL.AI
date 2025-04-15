# Multi-AI App Documentation

## Overview
This documentation provides comprehensive information about the improved Multi-AI application. The app integrates multiple AI models (OpenAI, Gemini, Claude, Llama, HuggingFace, OpenRouter) with a professional Streamlit interface featuring a sleek black and grey theme.

## Key Features

### User Interface
- Professional black and grey theme matching GensparkAI design
- Model icons/avatars for each AI service
- Visible memory display that updates with conversation context
- Collapsible/expandable view for each model's response
- Copy buttons for responses
- Mobile-responsive design

### AI Integration
- Support for multiple AI models:
  - OpenAI (GPT models)
  - Claude (Anthropic)
  - Gemini (Google)
  - Llama
  - HuggingFace models
  - OpenRouter
- Mixture-of-Agents feature for getting responses from multiple models simultaneously
- Intelligent model selection based on query type
- Fallback mechanisms when primary models fail

### Advanced Features
- Conversation memory with persistent storage
- File processing for various formats (PDF, CSV, text, code)
- Response synthesis using Llama
- User feedback collection and analysis
- Performance monitoring and metrics
- Response caching for improved performance

## Security Features
- Secure API key management with encryption
- Key validation and rotation support
- Usage logging for monitoring
- Proper authentication mechanisms

## Setup Instructions

### Local Development
1. Clone the repository:
   ```
   git clone https://github.com/jashmhta/ALL.AI.git
   cd ALL.AI
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   CLAUDE_API_KEY=your_claude_api_key
   LLAMA_API_KEY=your_llama_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_API_KEY_2=your_openrouter_api_key_2
   GEMINI_API_KEY=your_gemini_api_key
   BOTPRESS_WORKSPACE_ID=your_botpress_workspace_id
   ```

4. Run the application:
   ```
   streamlit run frontend/app.py
   ```

### Streamlit Share Deployment
1. Log in to your Streamlit Share account
2. Go to your app's settings
3. Add your actual API keys in the "Secrets" section using the following format:
   ```
   OPENAI_API_KEY = "your_openai_api_key"
   HUGGINGFACE_API_KEY = "your_huggingface_api_key"
   CLAUDE_API_KEY = "your_claude_api_key"
   LLAMA_API_KEY = "your_llama_api_key"
   OPENROUTER_API_KEY = "your_openrouter_api_key"
   OPENROUTER_API_KEY_2 = "your_openrouter_api_key_2"
   GEMINI_API_KEY = "your_gemini_api_key"
   BOTPRESS_WORKSPACE_ID = "your_botpress_workspace_id"
   ```

## Project Structure
- `/frontend`: Contains the Streamlit UI code
  - `app.py`: Main application file
- `/backend`: Contains the backend logic
  - `/clients`: API clients for different AI services
  - `/features`: Advanced features like conversation memory, file processing, etc.
  - `/utils`: Utility functions and classes
- `/data`: Data storage directories
  - `/cache`: Response cache
  - `/conversations`: Stored conversations
  - `/feedback`: User feedback
  - `/files`: Uploaded files

## Key Components

### KeyManager
Securely stores and manages API keys with encryption capabilities, key validation, and usage logging.

### ConversationMemory
Manages conversation history and context with methods for storing, retrieving, and managing conversation data.

### FileProcessor
Processes uploaded files, extracts text content from various file formats, and prepares it for AI analysis.

### FeedbackManager
Collects, stores, and analyzes user feedback to improve model selection.

### ModelOptimizer
Optimizes model selection based on feedback and performance metrics, providing recommendations for which models to use for different query types.

### SynthesisClient
Synthesizes responses from multiple AI models using Llama or another capable model to combine and analyze responses.

### CacheManager
Manages caching for the application, storing responses to avoid redundant API calls and improve performance.

### ResourceManager
Manages resource allocation and request throttling, ensuring fair distribution of resources and preventing overloading of API services.

### PerformanceMonitor
Monitors performance metrics including response times, success rates, and other performance indicators.

## Maintenance and Updates

### Adding New AI Models
To add a new AI model:
1. Create a new client in `/backend/clients/`
2. Update the main application to include the new model
3. Add the model to the ModelOptimizer for intelligent selection

### Updating API Keys
If you need to update API keys:
1. For local development, update your `.env` file
2. For Streamlit Share, update the secrets in the Streamlit Share dashboard

### Troubleshooting
- If you encounter API errors, check that your API keys are valid and properly configured
- If the app is slow, consider adjusting the cache settings or resource allocation
- For file processing issues, ensure you have the necessary dependencies installed

## Future Enhancements
Potential areas for future improvement:
- Adding more AI models as they become available
- Implementing more advanced synthesis techniques
- Enhancing the file processing capabilities
- Adding user authentication
- Implementing collaborative features

## Support
For issues or questions, please open an issue on the GitHub repository or contact the repository owner.
