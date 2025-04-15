# Multi-AI Application Documentation

## Overview

The Multi-AI Application is a powerful tool that integrates multiple AI APIs into a unified interface, providing enhanced capabilities, fallback mechanisms, and specialized functionality. This application allows users to interact with various AI models through a simple chat interface, with the ability to select specific models or let the system automatically choose the best available option.

## Architecture

### System Architecture

The application follows a modular architecture with the following components:

#### 1. Frontend Layer
- **Technology**: Streamlit
- **Purpose**: Provide a simple, interactive user interface for interacting with multiple AI models
- **Features**:
  - Chat interface
  - Model selection dropdown
  - Response display with formatting
  - Session history management
  - Advanced options (temperature, max tokens)
  - Dark theme styling

#### 2. Backend Layer
- **Technology**: Python
- **Purpose**: Handle API calls, manage routing, and process responses
- **Components**:
  - API client modules for each AI provider
  - Request router
  - Response processor
  - Error handler

#### 3. Integration Layer
- **Purpose**: Connect to multiple AI APIs and manage their interactions
- **Components**:
  - API key management
  - Request formatting
  - Response parsing
  - Fallback mechanisms

## API Integration

The application integrates with the following AI APIs:

### 1. Google Gemini
- **API Key Environment Variable**: `GEMINI_API_KEY`
- **Model Used**: gemini-1.5-flash
- **Client Implementation**: `backend/clients/gemini_client.py`

### 2. OpenAI
- **API Key Environment Variable**: `OPENAI_API_KEY`
- **Model Used**: gpt-3.5-turbo
- **Client Implementation**: `backend/clients/openai_client.py`

### 3. Hugging Face
- **API Key Environment Variable**: `HUGGINGFACE_API_KEY`
- **Model Used**: Configurable, defaults to google/flan-t5-xxl
- **Client Implementation**: `backend/clients/huggingface_client.py`

### 4. OpenRouter
- **API Key Environment Variable**: `OPENROUTER_API_KEY`
- **Model Used**: Configurable, defaults to openai/gpt-3.5-turbo
- **Client Implementation**: `backend/clients/openrouter_client.py`

### 5. Claude
- **API Key Environment Variable**: `CLAUDE_API_KEY`
- **Model Used**: claude-3-opus-20240229
- **Client Implementation**: `backend/clients/claude_client.py`

### 6. Llama
- **API Key Environment Variable**: `LLAMA_API_KEY`
- **Model Used**: llama-3-70b-instruct
- **Client Implementation**: `backend/clients/llama_client.py`

## Project Structure

```
ALL.AI/
├── .env                    # Environment variables (API keys)
├── README.md               # Project overview and instructions
├── requirements.txt        # Python dependencies
├── backend/
│   ├── __init__.py
│   ├── main.py             # Main application backend
│   ├── router.py           # Multi-AI router implementation
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── gemini_client.py
│   │   ├── openai_client.py
│   │   ├── huggingface_client.py
│   │   ├── openrouter_client.py
│   │   ├── claude_client.py
│   │   └── llama_client.py
│   └── utils/              # Utility functions
├── frontend/
│   ├── app.py              # Streamlit frontend application
│   ├── static/             # Static assets
│   ├── templates/          # HTML templates
│   └── history/            # Directory for saved chat histories
└── docs/                   # Additional documentation
```

## Installation and Setup

### Prerequisites

- Python 3.8+
- API keys for at least one of the supported AI services

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/jashmhta/ALL.AI.git
   cd ALL.AI
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure API keys:
   - Create a `.env` file in the root directory with your API keys:
   ```
   # OpenAI API
   OPENAI_API_KEY=your_openai_api_key

   # Google Gemini API
   GEMINI_API_KEY=your_gemini_api_key

   # Hugging Face API
   HUGGINGFACE_API_KEY=your_huggingface_api_key

   # OpenRouter API
   OPENROUTER_API_KEY=your_openrouter_api_key

   # Claude API
   CLAUDE_API_KEY=your_claude_api_key

   # Llama API
   LLAMA_API_KEY=your_llama_api_key

   # Botpress API
   BOTPRESS_API_KEY=your_botpress_api_key
   ```

4. Run the application:
   ```
   cd frontend
   streamlit run app.py
   ```

## Usage Guide

### Starting the Application

1. Navigate to the frontend directory:
   ```
   cd ALL.AI/frontend
   ```

2. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

3. The application will open in your default web browser at `http://localhost:8501`

### Using the Chat Interface

1. **Model Selection**: Use the dropdown in the sidebar to select a specific AI model or use "Auto (with fallback)" to let the system choose.

2. **Multiple Models**: Check the "Get responses from all available models" option to receive responses from all configured models simultaneously.

3. **Advanced Options**: Expand the "Advanced Options" section to adjust temperature and max tokens settings.

4. **Chat History**: Use the "Save History" and "Clear History" buttons to manage your conversation history.

5. **Asking Questions**: Type your question in the chat input field at the bottom of the page and press Enter to submit.

## Error Handling and Fallback Mechanisms

The application includes robust error handling and fallback mechanisms:

1. **API Error Handling**: Each client module includes try-except blocks to catch and handle API errors gracefully.

2. **Fallback System**: If a selected model fails, the system can automatically try other available models.

3. **Multiple Model Responses**: The application can request responses from multiple models in parallel, ensuring at least one successful response.

## Security Considerations

1. **API Key Storage**: API keys are stored in environment variables, not hardcoded in the application.

2. **Input Validation**: User inputs are validated before being sent to AI models.

3. **Error Messages**: Error messages are sanitized to prevent sensitive information disclosure.

## Extending the Application

### Adding New AI Models

To add a new AI model:

1. Create a new client module in the `backend/clients/` directory.
2. Implement the `generate_response` method following the same pattern as existing clients.
3. Update the `MultiAIApp` class in `backend/main.py` to initialize and use the new client.

### Customizing the UI

The Streamlit UI can be customized by modifying the `frontend/app.py` file:

1. Update the CSS in the `st.markdown` section to change the appearance.
2. Add new widgets or controls to the sidebar or main area.
3. Modify the chat display logic to change how messages are presented.

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your API keys are correctly set in the `.env` file.

2. **Model Availability**: Some models may be temporarily unavailable or have rate limits.

3. **Dependency Issues**: Make sure all required packages are installed using `pip install -r requirements.txt`.

### Debugging

1. Check the console output for error messages.

2. Enable verbose logging by adding `import logging; logging.basicConfig(level=logging.DEBUG)` to the top of `app.py`.

3. Test individual API clients directly to isolate issues.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all the AI providers for their APIs
- Special thanks to the open-source community for their contributions
