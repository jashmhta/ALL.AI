# ALL.AI - Multi-AI Application

A powerful application that integrates multiple AI APIs into a unified interface, providing enhanced capabilities, fallback options, and specialized functionality.

## Features

- **Multiple AI Models**: Integrates with Google Gemini, OpenAI, Hugging Face, Claude, Llama, and more
- **Unified Interface**: Simple chat interface for interacting with all AI models
- **Fallback Mechanisms**: Automatically switches to alternative models when primary model fails
- **Model Selection**: Choose specific AI models or let the system select the best available
- **Session History**: Save and manage conversation history
- **Advanced Options**: Configure temperature, max tokens, and other parameters

## Architecture

### System Architecture

#### 1. Frontend Layer
- **Technology**: Streamlit
- **Purpose**: Provide a simple, interactive user interface for interacting with multiple AI models
- **Features**:
  - Chat interface
  - Model selection dropdown
  - Response display with formatting
  - Session history management

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

## Getting Started

### Prerequisites

- Python 3.8+
- API keys for at least one of the supported AI services

### Installation

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
   - Create a `.env` file in the root directory
   - Add your API keys (see `.env.example` for format)

4. Run the application:
   ```
   cd frontend
   streamlit run app.py
   ```

## Supported AI Services

- **Google Gemini**: Advanced language model from Google
- **OpenAI**: GPT models for text generation
- **Hugging Face**: Access to thousands of open-source models
- **Claude**: Anthropic's conversational AI assistant
- **Llama**: Meta's open-source large language model
- **OpenRouter**: Single API endpoint for multiple AI models
- **Botpress**: Conversational AI platform

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all the AI providers for their APIs
- Special thanks to the open-source community for their contributions
