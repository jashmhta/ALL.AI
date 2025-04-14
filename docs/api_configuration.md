# API Configuration Guide

This document provides instructions for configuring the API keys required by the Multi-AI application.

## Supported AI Services

The Multi-AI application supports integration with the following AI services:

1. **Google Gemini**
2. **OpenAI**
3. **Hugging Face**
4. **OpenRouter**
5. **Claude (Anthropic)**
6. **Llama**
7. **Botpress**

## API Key Configuration

API keys are stored in a `.env` file in the root directory of the project. This file is not committed to the repository for security reasons.

### Creating the .env File

1. Create a file named `.env` in the root directory of the project.
2. Add your API keys in the following format:

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

### Obtaining API Keys

#### Google Gemini API
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Create or sign in to your Google account
3. Navigate to the API keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

#### OpenAI API
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create or sign in to your OpenAI account
3. Navigate to the API keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

#### Hugging Face API
1. Visit [Hugging Face](https://huggingface.co/)
2. Create or sign in to your Hugging Face account
3. Navigate to your profile settings
4. Go to the Access Tokens section
5. Create a new token
6. Copy the token and add it to your `.env` file

#### OpenRouter API
1. Visit [OpenRouter](https://openrouter.ai/)
2. Create or sign in to your account
3. Navigate to the API keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

#### Claude API
1. Visit [Anthropic](https://www.anthropic.com/api)
2. Create or sign in to your Anthropic account
3. Navigate to the API keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

#### Llama API
1. Obtain your Llama API key from the provider
2. Add it to your `.env` file

#### Botpress API
1. Visit [Botpress](https://botpress.com/)
2. Create or sign in to your Botpress account
3. Navigate to the API keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## Security Considerations

- **Never commit your `.env` file to version control**
- **Do not share your API keys with others**
- **Regularly rotate your API keys for enhanced security**
- **Use environment variables in production environments**

## Troubleshooting

If you encounter issues with API keys:

1. Verify that the API key is correctly formatted and has no extra spaces
2. Ensure the API key is active and not expired
3. Check if you have reached any rate limits for the service
4. Verify that the service is available and not experiencing downtime
